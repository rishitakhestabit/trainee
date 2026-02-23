# src/pipelines/image_ingest.py
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import faiss
import pytesseract
import fitz  # PyMuPDF
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

from src.embeddings.clip_embedder import CLIPEmbedder


# Your images folder
IMAGES_DIR = Path("src/data/images")

OUT_DIR = Path("src/data/vectorstore")
OUT_DIR.mkdir(parents=True, exist_ok=True)

INDEX_PATH = OUT_DIR / "image_index.faiss"
META_PATH = OUT_DIR / "image_index_meta.json"


@dataclass
class IngestConfig:
    tags: List[str] = None
    ocr_lang: str = "eng"
    blip_model: str = "Salesforce/blip-image-captioning-base"
    dpi: int = 200

    def __post_init__(self):
        if self.tags is None:
            self.tags = ["week7", "image-rag"]


def iter_images_and_pdf_pages(images_dir: Path, dpi: int) -> List[Tuple[Image.Image, Dict[str, Any]]]:
    """
    Loads:
      - PNG/JPG/JPEG from src/data/images/
      - PDF pages (scanned PDFs) from src/data/images/
    Returns list of (PIL.Image, meta)
    """
    out: List[Tuple[Image.Image, Dict[str, Any]]] = []
    exts = {".png", ".jpg", ".jpeg"}

    if not images_dir.exists():
        raise FileNotFoundError(f"Images directory not found: {images_dir}")

    files = sorted([p for p in images_dir.rglob("*") if p.is_file()])

    for p in files:
        suf = p.suffix.lower()

        if suf in exts:
            img = Image.open(p)
            meta = {"source": str(p), "type": "image", "page": None}
            out.append((img, meta))

        elif suf == ".pdf":
            doc = fitz.open(str(p))
            for page_idx in range(len(doc)):
                page = doc.load_page(page_idx)
                pix = page.get_pixmap(dpi=dpi)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                meta = {"source": str(p), "type": "pdf", "page": page_idx + 1}
                out.append((img, meta))

    return out


def ocr_text(image: Image.Image, lang: str = "eng") -> str:
    if image.mode != "RGB":
        image = image.convert("RGB")
    text = pytesseract.image_to_string(image, lang=lang)
    return " ".join(text.split())


class BLIPCaptioner:
    def __init__(self, model_name: str):
        # Warnings about tied weights / unexpected keys are normal and safe to ignore
        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(model_name)
        self.model.eval()

    def caption(self, image: Image.Image) -> str:
        if image.mode != "RGB":
            image = image.convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt")
        out = self.model.generate(**inputs, max_new_tokens=30)
        return self.processor.decode(out[0], skip_special_tokens=True).strip()


def main():
    cfg = IngestConfig()

    clip = CLIPEmbedder()
    blip = BLIPCaptioner(cfg.blip_model)

    items = iter_images_and_pdf_pages(IMAGES_DIR, dpi=cfg.dpi)
    if not items:
        raise RuntimeError(
            f"No images/PDFs found in {IMAGES_DIR}. Put .png/.jpg/.pdf files there and rerun."
        )

    vectors: List[np.ndarray] = []
    records: List[Dict[str, Any]] = []

    for idx, (img, base_meta) in enumerate(items):
        text = ocr_text(img, lang=cfg.ocr_lang)
        cap = blip.caption(img)
        vec = clip.embed_image(img)

        meta = {
            **base_meta,
            "chunk_id": idx,
            "tags": cfg.tags,
            "ocr_text": text,
            "caption": cap,
        }

        combined_text = f"CAPTION: {cap}\nOCR: {text}".strip()
        records.append({"text": combined_text, "meta": meta})
        vectors.append(vec)

        print(f"[{idx+1}/{len(items)}] indexed: {base_meta['source']} page={base_meta['page']}")

    X = np.vstack(vectors).astype("float32")  # (n, d)

    # cosine similarity search = inner product on normalized vectors
    index = faiss.IndexFlatIP(X.shape[1])
    index.add(X)

    faiss.write_index(index, str(INDEX_PATH))
    META_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")

    print("\nDONE → Image index created")
    print("FAISS:", INDEX_PATH)
    print("META :", META_PATH)
    print("Total vectors:", X.shape[0], "dim:", X.shape[1])


if __name__ == "__main__":
    main()