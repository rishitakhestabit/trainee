# src/retriever/query_engine.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

from src.embeddings.embedder import Embedder
from src.vectorstore.faiss_store import FaissVectorStore, FaissPaths

INDEX_PATH = Path("src/data/vectorstore/index.faiss")
META_PATH = Path("src/data/vectorstore/index_meta.json")


class QueryEngine:

    def __init__(
        self,
        index_path: Path = INDEX_PATH,
        meta_path: Path = META_PATH,
    ):
        self.embedder = Embedder()
        self.store = FaissVectorStore(FaissPaths(index_path, meta_path))
        self.store.load()

    def query(self, q: str, top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        q_vec = self.embedder.embed_query(q)
        # NOTE: your store.search currently uses parameter name `k`
        return self.store.search(q_vec, k=top_k)

    def build_context(
        self,
        results: List[Tuple[float, Dict[str, Any]]],
        max_chars_per_chunk: int = 1200,
    ) -> str:
        """
        Turns retrieved chunks into a single context string that is ready
        to feed into an LLM later (Day-2/Day-5).
        """
        blocks = []
        for i, (score, item) in enumerate(results, 1):
            meta = item.get("meta", {})
            source = meta.get("source", "unknown")
            page = meta.get("page", None)
            ctype = meta.get("type", None)
            chunk_id = meta.get("chunk_id", None)

            header_parts = [f"#{i}", f"score={score:.4f}", f"source={source}"]
            if page is not None:
                header_parts.append(f"page={page}")
            if ctype is not None:
                header_parts.append(f"type={ctype}")
            if chunk_id is not None:
                header_parts.append(f"chunk={chunk_id}")

            header = " | ".join(header_parts)
            text = (item.get("text") or "").strip()
            if len(text) > max_chars_per_chunk:
                text = text[:max_chars_per_chunk].rstrip() + "…"

            blocks.append(f"{header}\n{text}")

        return "\n\n" + ("\n\n" + "-" * 80 + "\n\n").join(blocks) + "\n"

    def pretty_print(
        self,
        results: List[Tuple[float, Dict[str, Any]]],
        max_preview_chars: int = 500,
    ) -> None:
        """
        Friendly terminal output for retrieval debugging.
        """
        for i, (score, item) in enumerate(results, 1):
            meta = item.get("meta", {})
            print("\n" + "=" * 90)
            print(f"[{i}] Score: {score:.4f}")
            print(
                f"source={meta.get('source')} | page={meta.get('page')} | "
                f"type={meta.get('type')} | chunk_id={meta.get('chunk_id')}"
            )
            text = (item.get("text") or "").strip()
            print(text[:max_preview_chars] + ("…" if len(text) > max_preview_chars else ""))


if __name__ == "__main__":
    qe = QueryEngine()
    print("Retriever ready. Ask questions (type 'exit' to quit).")

    while True:
        q = input("\nAsk: ").strip()
        if not q:
            continue
        if q.lower() in {"exit", "quit"}:
            print("Bye")
            break

        results = qe.query(q, top_k=5)

        # 1) Print retrieval results
        qe.pretty_print(results)

        # 2) Also show the combined context (useful for LLM later)
        context = qe.build_context(results)
        print("\n Context (ready for generator):")
        print(context)
