from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.documents import Document

from src.retriever.hybrid_retriever import HybridRetriever
from src.retriever.reranker import Reranker


@dataclass
class ContextConfig:
    top_k: int = 5
    year: Optional[str] = None
    doc_type: Optional[str] = None

    # Context window optimization
    max_context_tokens: int = 1800
    include_metadata_header: bool = True

    # Candidate pool size in retriever is controlled there, but we still rerank top_k final
    show_preview_chars: int = 240


def _hash_text(text: str) -> str:
    t = " ".join(text.strip().lower().split())
    return hashlib.md5(t.encode("utf-8")).hexdigest()


def deduplicate(docs: List[Document]) -> List[Document]:
    seen = set()
    out: List[Document] = []
    for d in docs:
        h = _hash_text(d.page_content)
        if h in seen:
            continue
        seen.add(h)
        out.append(d)
    return out


def _approx_tokens(text: str) -> int:
    # good enough for budgeting; if you used tokenizer earlier, this is fine for Day-2
    return max(1, int(len(text.split()) / 0.75))


def build_context(
    docs: List[Document],
    cfg: ContextConfig,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Context window optimization:
    pack chunks until token budget is reached.
    Outputs:
      - context_text (LLM-ready)
      - sources (traceability)
    """
    context_parts: List[str] = []
    sources: List[Dict[str, Any]] = []
    used = 0

    for i, d in enumerate(docs, start=1):
        src = d.metadata.get("source", "unknown")
        page = d.metadata.get("page", None)
        year = d.metadata.get("year", None)
        doc_type = d.metadata.get("type", None)
        tags = d.metadata.get("tags", [])

        header = ""
        if cfg.include_metadata_header:
            header = f"[{i}] source={src} | page={page} | year={year} | type={doc_type} | tags={tags}\n"

        MAX_CHARS = 400  # shorten terminal output

        body_full = d.page_content.strip()
        body_preview = body_full[:MAX_CHARS] + ("..." if len(body_full) > MAX_CHARS else "")

        block = header + body_preview + "\n"

        t = _approx_tokens(block)
        if used + t > cfg.max_context_tokens:
            break

        context_parts.append(block)
        used += t

        sources.append(
            {
                "rank": i,
                "source": src,
                "page": page,
                "year": year,
                "type": doc_type,
                "tags": tags,
                "preview": body_full[: cfg.show_preview_chars],
            }
        )

    return "\n---\n".join(context_parts).strip(), sources


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Day-2 Context Builder Runner (Hybrid + MMR + Rerank + Dedup + Context Budget)")
    p.add_argument("--query", type=str, default=None)
    p.add_argument("--top_k", type=int, default=5)
    p.add_argument("--year", type=str, default=None)
    p.add_argument("--type", dest="doc_type", type=str, default=None)
    p.add_argument("--max_context_tokens", type=int, default=1800)
    p.add_argument("--no_headers", action="store_true")
    return p.parse_args()


def run_once(query: str, cfg: ContextConfig) -> None:
    filters: Dict[str, Any] = {}
    if cfg.year:
        filters["year"] = cfg.year
    if cfg.doc_type:
        filters["type"] = cfg.doc_type

    # 1) Hybrid retrieve (BM25+FAISS) + MMR candidates
    retriever = HybridRetriever()
    candidates = retriever.retrieve_candidates(query, top_k=cfg.top_k, filters=filters)

    if not candidates:
        print("No chunks matched filters. Check year/type metadata or filenames.")
        return

    # 2) Rerank (cross-encoder / cosine fallback)
    reranker = Reranker()
    reranked = reranker.rerank(query, candidates, top_k=cfg.top_k)

    final_docs = [d for d, _ in reranked]

    # 3) Dedup
    final_docs = deduplicate(final_docs)

    # 4) Context window optimization (token budget packing)
    context_text, sources = build_context(final_docs, cfg)

    # Output
    print("\n===== FINAL CONTEXT (Day-2) =====\n")
    print(context_text if context_text else "(Context empty after budgeting)")

    print("\n===== SOURCES (Traceable) =====")
    for s in sources:
        print(f"{s['rank']}. {s['source']} (page {s['page']}) year={s['year']} type={s['type']}")
    print("")


def main():
    args = parse_args()

    cfg = ContextConfig(
        top_k=args.top_k,
        year=args.year,
        doc_type=args.doc_type,
        max_context_tokens=args.max_context_tokens,
        include_metadata_header=not args.no_headers,
    )

    # If no --query given, run interactive mode (because you said you will only run this file)
    if not args.query:
        print("\n=== Day-2 Runner: context_builder ===")
        print("Hybrid (BM25+FAISS) + Filters + MMR + Rerank + Dedup + Context Budget")
        print("Type query and press Enter. Ctrl+C to exit.\n")
        try:
            while True:
                q = input("Query> ").strip()
                if not q:
                    continue
                run_once(q, cfg)
        except KeyboardInterrupt:
            print("\nExiting Day-2.\n")
        return

    run_once(args.query, cfg)


if __name__ == "__main__":
    main()