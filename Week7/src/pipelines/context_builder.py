# src/pipelines/context_builder.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional

from src.retriever.hybrid_retriever import HybridRetriever


@dataclass
class ContextConfig:
    max_chars_per_chunk: int = 1200
    separator: str = "\n\n" + ("-" * 90) + "\n\n"


def build_context(
    results: List[Tuple[float, Dict[str, Any]]],
    config: ContextConfig = ContextConfig(),
) -> str:
    """
    Builds a traceable context string to send into the Generator stage.
    """
    blocks = []

    for i, (score, item) in enumerate(results, 1):
        meta = item.get("meta", {})
        source = meta.get("source", "unknown")
        page = meta.get("page", None)
        ctype = meta.get("type", None)
        chunk_id = meta.get("chunk_id", None)

        header = f"[{i}] score={score:.4f} | source={source}"
        if page is not None:
            header += f" | page={page}"
        if ctype is not None:
            header += f" | type={ctype}"
        if chunk_id is not None:
            header += f" | chunk={chunk_id}"

        text = (item.get("text") or "").strip()
        if len(text) > config.max_chars_per_chunk:
            text = text[:config.max_chars_per_chunk].rstrip() + "…"

        blocks.append(header + "\n" + text)

    return config.separator.join(blocks)


def parse_filters(raw: str) -> Optional[Dict[str, Any]]:
    """
    Input format (simple):
      type=pdf, source_contains=astrazeneca, tag=rag

    Empty input => None
    """
    raw = raw.strip()
    if not raw:
        return None

    out: Dict[str, Any] = {}
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    for p in parts:
        if "=" not in p:
            continue
        k, v = p.split("=", 1)
        out[k.strip()] = v.strip()
    return out or None


if __name__ == "__main__":
    retriever = HybridRetriever()

    # Fixed retrieval configuration (taskflow requirement)
    TOP_K = 5
    FILTERS = {"type": "pdf"}   # adapt if you later add year/policy metadata

    print("Day-2 Hybrid Retriever Ready (type 'exit' to quit)")

    while True:
        query = input("\nEnter your question: ").strip()

        if query.lower() in {"exit", "quit"}:
            print("Exiting...")
            break

        if not query:
            continue

        hits = retriever.retrieve(query, top_k=TOP_K, filters=FILTERS)

        print("\nTOP HITS:")
        for s, it in hits:
            print(f"{s:.4f}", it["meta"])

        print("\nTRACEABLE CONTEXT:\n")
        print(build_context(hits))