from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import numpy as np
from PIL import Image

from src.embeddings.clip_embedder import CLIPConfig, CLIPEembedder


MM_DIR = Path("src/multimodal_vectorstore")
INDEX_PATH = MM_DIR / "images.faiss"
META_PATH = MM_DIR / "images_meta.jsonl"


@dataclass
class SearchConfig:
    top_k: int = 5
    clip_model: str = "openai/clip-vit-base-patch32"


def _load_meta(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run: python -m src.pipelines.image_ingest")
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def _load_faiss(path: Path):
    import faiss
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run: python -m src.pipelines.image_ingest")
    return faiss.read_index(str(path))


def _safe_open_image(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def _search(index, qvec: np.ndarray, top_k: int) -> Tuple[np.ndarray, np.ndarray]:
    q = qvec.astype(np.float32)[None, :]
    scores, idxs = index.search(q, top_k)
    return scores[0], idxs[0]


SIMILARITY_THRESHOLD = 0.25 

def _make_hits(meta: List[Dict[str, Any]], scores: np.ndarray, idxs: np.ndarray, top_k: int) -> List[Dict[str, Any]]:
    hits: List[Dict[str, Any]] = []
    for rank, (s, i) in enumerate(zip(scores, idxs), start=1):
        if len(hits) >= top_k:
            break
        if int(i) < 0:
            continue
        if float(s) < SIMILARITY_THRESHOLD:  # skip low similarity
            continue
        row = meta[int(i)]
        hits.append(
            {
                "rank": rank,
                "score": float(s),
                "source": row.get("source"),
                "page": row.get("page"),
                "kind": row.get("kind"),
                "caption": row.get("caption", ""),
                "ocr_text_preview": (row.get("ocr_text", "") or "")[:300],
                "path": row.get("path"),  # if you stored it in ingest meta
            }
        )
    return hits


def _print_results(hits: List[Dict[str, Any]], mode: str) -> None:
    if not hits:
        print("\n(No results)\n")
        return

    if mode in ("text2img", "img2img"):
        print("\n===== TOP MATCHING IMAGES/PAGES =====\n")
        for h in hits:
            print(f"[{h['rank']}] score={h['score']:.4f}")
            print(f"    source: {h['source']}")
            print(f"    page  : {h['page']} | kind: {h['kind']}")
            if h["caption"]:
                print(f"    caption: {h['caption']}")
            if h["ocr_text_preview"]:
                print(f"    ocr    : {h['ocr_text_preview']}")
            print("")
    else:
        print("\n===== IMAGE - TEXT ANSWER (Context) =====\n")
        for h in hits:
            print(f"[{h['rank']}] score={h['score']:.4f}")
            print(f"    source: {h['source']}")
            print(f"    page  : {h['page']} | kind: {h['kind']}")
            if h["caption"]:
                print(f"\nCAPTION:\n{h['caption']}\n")
            if h["ocr_text_preview"]:
                print(f"OCR (preview):\n{h['ocr_text_preview']}\n")
            print("--------------------------------------------------")

class ImageSearchEngine:
    def __init__(self, cfg: Optional[SearchConfig] = None):
        self.cfg = cfg or SearchConfig()
        self.meta = _load_meta(META_PATH)
        self.index = _load_faiss(INDEX_PATH)
        self.clip = CLIPEembedder(CLIPConfig(model_name=self.cfg.clip_model))

    def text_to_image(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        qvec = self.clip.embed_text(query)
        scores, idxs = _search(self.index, qvec, top_k)
        return _make_hits(self.meta, scores, idxs, top_k)

    def image_to_image(self, image_path: str, top_k: int = 5) -> List[Dict[str, Any]]:
        p = Path(image_path)
        if not p.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        img = _safe_open_image(p)
        qvec = self.clip.embed_image(img)
        scores, idxs = _search(self.index, qvec, top_k)
        return _make_hits(self.meta, scores, idxs, top_k)

    def image_to_text(self, image_path: str, top_k: int = 5) -> str:
        hits = self.image_to_image(image_path, top_k=top_k)
        # "answer" = captions + OCR previews (simple baseline)
        lines: List[str] = []
        for h in hits:
            if h.get("caption"):
                lines.append(f"- {h['caption']}")
            if h.get("ocr_text_preview"):
                lines.append(f"  OCR: {h['ocr_text_preview']}")
        return "\n".join(lines).strip()

_ENGINE: Optional[ImageSearchEngine] = None

def _get_engine() -> ImageSearchEngine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = ImageSearchEngine()
    return _ENGINE


def search_text(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    return _get_engine().text_to_image(query, top_k=top_k)


def search_image(image_path: str, top_k: int = 5) -> List[Dict[str, Any]]:
    return _get_engine().image_to_image(image_path, top_k=top_k)


def image_to_text_answer(image_path: str, top_k: int = 5) -> str:
    return _get_engine().image_to_text(image_path, top_k=top_k)



def parse_args():
    p = argparse.ArgumentParser(description="Day-3 Image Search (CLIP + FAISS).")
    p.add_argument("--mode", type=str, default=None, choices=["text2img", "img2img", "img2text"])
    p.add_argument("--query", type=str, default=None)
    p.add_argument("--image", type=str, default=None)
    p.add_argument("--top_k", type=int, default=5)
    return p.parse_args()


def _interactive_loop(engine: ImageSearchEngine) -> None:
    print("\n=== DAY 3 — IMAGE RAG (MULTIMODAL SEARCH) ===")
    print("Menu repeats after every search. Press Ctrl+C anytime to exit.\n")

    while True:
        print("\nChoose an option:")
        print("1) Text → Image")
        print("2) Image → Image")
        print("3) Image → Text Answer")
        print("4) Exit")

        choice = input("Enter choice (1/2/3/4): ").strip()

        if choice == "4":
            print("\nExiting.\n")
            break

        if choice == "1":
            query = input("Enter text query: ").strip()
            if not query:
                print("Empty query. Try again.")
                continue
            hits = engine.text_to_image(query, top_k=engine.cfg.top_k)
            _print_results(hits, "text2img")

        elif choice == "2":
            img_path = input("Enter image path (e.g. src/data/images/x.jpg): ").strip()
            try:
                hits = engine.image_to_image(img_path, top_k=engine.cfg.top_k)
                _print_results(hits, "img2img")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "3":
            img_path = input("Enter image path (e.g. src/data/images/x.jpg): ").strip()
            try:
                hits = engine.image_to_image(img_path, top_k=engine.cfg.top_k)
                _print_results(hits, "img2text")
            except Exception as e:
                print(f"Error: {e}")

        else:
            print("Invalid choice. Enter 1/2/3/4.")
            continue


def main():
    args = parse_args()
    engine = ImageSearchEngine(SearchConfig(top_k=args.top_k))

    if args.mode:
        if args.mode == "text2img":
            if not args.query:
                raise SystemExit("Provide --query for text2img")
            hits = engine.text_to_image(args.query, top_k=args.top_k)
            _print_results(hits, "text2img")
            return

        if not args.image:
            raise SystemExit("Provide --image for img2img/img2text")

        if args.mode == "img2img":
            hits = engine.image_to_image(args.image, top_k=args.top_k)
            _print_results(hits, "img2img")
            return

        if args.mode == "img2text":
            hits = engine.image_to_image(args.image, top_k=args.top_k)
            _print_results(hits, "img2text")
            return

    try:
        _interactive_loop(engine)
    except KeyboardInterrupt:
        print("\n\nExiting (Ctrl+C)\n")


if __name__ == "__main__":
    main()