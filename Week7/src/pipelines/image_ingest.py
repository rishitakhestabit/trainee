from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

from src.embeddings.clip_embedder import CLIPConfig, CLIPEembedder


IMAGES_DIR = Path("src/data/images")  #  your folder
MM_DIR = Path("src/multimodal_vectorstore")
MM_DIR.mkdir(parents=True, exist_ok=True)

INDEX_PATH = MM_DIR / "images.faiss"
META_PATH = MM_DIR / "images_meta.jsonl"


@dataclass
class ImageIngestConfig:
    images_dir: Path = IMAGES_DIR
    top_pages_per_pdf: Optional[int] = None  # None = all pages
    clip_model: str = "openai/clip-vit-base-patch32"
    blip_model: str = "Salesforce/blip-image-captioning-base"
    do_ocr: bool = True
    do_caption: bool = True


def _is_image(p: Path) -> bool:
    return p.suffix.lower() in {".png", ".jpg", ".jpeg"}


def _is_pdf(p: Path) -> bool:
    return p.suffix.lower() == ".pdf"


def _safe_load_image(path: Path) -> Optional[Image.Image]:
    try:
        return Image.open(path).convert("RGB")
    except Exception:
        return None


def _render_pdf_to_images(pdf_path: Path, max_pages: Optional[int]) -> List[Tuple[int, Image.Image]]:
    """
    Render PDF pages -> PIL images. Requires PyMuPDF.
    Returns list of (page_number, pil_image)
    """
    try:
        import fitz  # PyMuPDF
    except Exception as e:
        raise RuntimeError("PyMuPDF not installed. Run: pip install pymupdf") from e

    doc = fitz.open(str(pdf_path))
    out: List[Tuple[int, Image.Image]] = []

    total = doc.page_count
    limit = total if max_pages is None else min(total, max_pages)

    for i in range(limit):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        out.append((i, img))

    return out


def _ocr_text(pil_img: Image.Image) -> str:
    try:
        import pytesseract
        return (pytesseract.image_to_string(pil_img) or "").strip()
    except Exception:
        return ""


class _BLIPCaptioner:
    def __init__(self, model_name: str):
        import torch
        from transformers import BlipProcessor, BlipForConditionalGeneration

        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def caption(self, pil_img: Image.Image) -> str:
        inputs = self.processor(images=pil_img, return_tensors="pt").to(self.device)
        with self.torch.no_grad():
            out = self.model.generate(**inputs, max_new_tokens=40)
        return (self.processor.decode(out[0], skip_special_tokens=True) or "").strip()


def _save_meta_jsonl(rows: List[Dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _build_faiss(vectors: np.ndarray):
    import faiss
    vectors = vectors.astype(np.float32)
    d = vectors.shape[1]
    index = faiss.IndexFlatIP(d)  # cosine similarity when vectors are normalized
    index.add(vectors)
    return index


def parse_args():
    p = argparse.ArgumentParser(description="Day-3 Image Ingest: OCR + CLIP + BLIP + FAISS")
    p.add_argument("--images_dir", type=str, default=str(IMAGES_DIR))
    p.add_argument("--max_pdf_pages", type=int, default=0, help="0 = all pages")
    p.add_argument("--no_ocr", action="store_true")
    p.add_argument("--no_caption", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    cfg = ImageIngestConfig(
        images_dir=Path(args.images_dir),
        top_pages_per_pdf=None if args.max_pdf_pages == 0 else args.max_pdf_pages,
        do_ocr=not args.no_ocr,
        do_caption=not args.no_caption,
    )

    if not cfg.images_dir.exists():
        raise SystemExit(f"Folder not found: {cfg.images_dir}")

    clip = CLIPEembedder(CLIPConfig(model_name=cfg.clip_model))

    captioner = None
    if cfg.do_caption:
        try:
            captioner = _BLIPCaptioner(cfg.blip_model)
        except Exception:
            captioner = None  # graceful degrade

    images: List[Image.Image] = []
    metas: List[Dict[str, Any]] = []

    files = [p for p in cfg.images_dir.rglob("*") if p.is_file()]
    files.sort()

    for fp in files:
        if _is_image(fp):
            img = _safe_load_image(fp)
            if img is None:
                continue

            ocr = _ocr_text(img) if cfg.do_ocr else ""
            cap = captioner.caption(img) if captioner is not None else ""

            metas.append(
                {
                    "id": len(metas),
                    "source": str(fp),
                    "kind": "image",
                    "page": None,
                    "ocr_text": ocr,
                    "caption": cap,
                }
            )
            images.append(img)

        elif _is_pdf(fp):
            try:
                rendered = _render_pdf_to_images(fp, cfg.top_pages_per_pdf)
            except Exception:
                continue

            for page_num, img in rendered:
                ocr = _ocr_text(img) if cfg.do_ocr else ""
                cap = captioner.caption(img) if captioner is not None else ""

                metas.append(
                    {
                        "id": len(metas),
                        "source": str(fp),
                        "kind": "pdf_page",
                        "page": int(page_num),
                        "ocr_text": ocr,
                        "caption": cap,
                    }
                )
                images.append(img)

    if not images:
        print("[IMAGE_INGEST] No images or PDF pages found in:", cfg.images_dir)
        return

    vecs = clip.embed_images(images)  # (n, d) normalized

    index = _build_faiss(vecs)

    import faiss
    faiss.write_index(index, str(INDEX_PATH))
    _save_meta_jsonl(metas, META_PATH)

    print(f"[IMAGE_INGEST] Scanned folder: {cfg.images_dir}")
    print(f"[IMAGE_INGEST] Total indexed items: {len(metas)}")
    print(f"[IMAGE_INGEST] Saved FAISS: {INDEX_PATH}")
    print(f"[IMAGE_INGEST] Saved metadata: {META_PATH}")
    if cfg.do_caption and captioner is None:
        print("[IMAGE_INGEST] NOTE: BLIP captioning unavailable (model load failed). Captions skipped.")
    if cfg.do_ocr:
        print("[IMAGE_INGEST] OCR enabled (requires system tesseract).")


if __name__ == "__main__":
    main()