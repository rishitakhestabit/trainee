# src/retriever/image_search.py
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import faiss
import numpy as np
from PIL import Image

from src.embeddings.clip_embedder import CLIPEmbedder


INDEX_PATH = Path("src/data/vectorstore/image_index.faiss")
META_PATH = Path("src/data/vectorstore/image_index_meta.json")


@dataclass
class SearchConfig:
    top_k: int = 5


def _passes_filters(meta: Dict[str, Any], filters: Optional[Dict[str, Any]]) -> bool:
    if not filters:
        return True
    for k, v in filters.items():
        if k == "source_contains":
            if str(v).lower() not in str(meta.get("source", "")).lower():
                return False
        elif k == "tag":
            tags = meta.get("tags", []) or []
            if v not in tags:
                return False
        else:
            if str(meta.get(k, "")).lower() != str(v).lower():
                return False
    return True


class ImageSearcher:
    def __init__(self):
        if not INDEX_PATH.exists():
            raise FileNotFoundError(f"Missing index: {INDEX_PATH}. Run image_ingest first.")
        if not META_PATH.exists():
            raise FileNotFoundError(f"Missing meta: {META_PATH}. Run image_ingest first.")

        self.embedder = CLIPEmbedder()
        self.index = faiss.read_index(str(INDEX_PATH))
        self.items: List[Dict[str, Any]] = json.loads(META_PATH.read_text(encoding="utf-8"))

    def _search_vec(self, vec: np.ndarray, top_k: int) -> List[Tuple[float, Dict[str, Any]]]:
        q = vec.astype("float32")[None, :]
        scores, idxs = self.index.search(q, top_k)
        out = []
        for s, i in zip(scores[0].tolist(), idxs[0].tolist()):
            if i == -1:
                continue
            out.append((float(s), self.items[i]))
        return out

    def text_to_image(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None):
        q_vec = self.embedder.embed_text(query)
        hits = self._search_vec(q_vec, top_k=top_k * 5)
        if filters:
            hits = [(s, it) for s, it in hits if _passes_filters(it.get("meta", {}), filters)]
        return hits[:top_k]

    def image_to_image(self, image_path: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None):
        img = Image.open(image_path)
        v = self.embedder.embed_image(img)
        hits = self._search_vec(v, top_k=top_k * 5)
        if filters:
            hits = [(s, it) for s, it in hits if _passes_filters(it.get("meta", {}), filters)]
        return hits[:top_k]

    def image_to_text_answer(self, image_path: str, top_k: int = 5) -> str:
        """
        Returns an evidence-based explanation context built from caption + OCR
        of retrieved similar images. (LLM generation comes later days.)
        """
        hits = self.image_to_image(image_path, top_k=top_k)
        lines = [f"Query image: {image_path}", "\nRetrieved evidence:\n"]

        for i, (score, item) in enumerate(hits, 1):
            meta = item.get("meta", {})
            cap = meta.get("caption", "")
            ocr = meta.get("ocr_text", "")

            lines.append(
                f"[{i}] score={score:.4f} | source={meta.get('source')} | page={meta.get('page')} | type={meta.get('type')}"
            )
            if cap:
                lines.append(f"Caption: {cap}")
            if ocr:
                short = ocr[:700] + ("…" if len(ocr) > 700 else "")
                lines.append(f"OCR: {short}")
            lines.append("-" * 90)

        return "\n".join(lines)


if __name__ == "__main__":
    s = ImageSearcher()
    print("Image Search Ready")
    print("Modes: 1) text->image  2) image->image  3) image->text answer  (type 'exit' to quit)")

    while True:
        mode = input("\nMode (1/2/3): ").strip()
        if mode.lower() in {"exit", "quit"}:
            break

        if mode == "1":
            q = input("Text query: ").strip()
            hits = s.text_to_image(q, top_k=5)
            for score, item in hits:
                print("\nScore:", score)
                print(item["meta"])
                print(item["text"][:250])

        elif mode == "2":
            p = input("Image path: ").strip()
            hits = s.image_to_image(p, top_k=5)
            for score, item in hits:
                print("\nScore:", score)
                print(item["meta"])
                print(item["text"][:250])

        elif mode == "3":
            p = input("Image path: ").strip()
            print("\n" + s.image_to_text_answer(p, top_k=5))

        else:
            print("Choose 1, 2, or 3.")