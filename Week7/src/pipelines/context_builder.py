from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

from langchain_core.documents import Document

from src.retriever.hybrid_retriever import HybridRetriever
from src.retriever.reranker import Reranker


# ================= CONFIG =================
@dataclass
class ContextConfig:
    top_k: int = 5
    year: Optional[str] = None
    doc_type: Optional[str] = None
    max_context_tokens: int = 1800
    include_metadata_header: bool = True
    show_preview_chars: int = 240


# ================= SAFE NORMALIZER =================
def _safe_docs(
    docs: List[Union[Document, Tuple[Document, float]]]
) -> List[Document]:
    out: List[Document] = []
    for d in docs:
        try:
            if isinstance(d, tuple):
                if len(d) > 0 and isinstance(d[0], Document):
                    out.append(d[0])
            elif isinstance(d, Document):
                out.append(d)
        except Exception:
            continue
    return out


# ================= HASH =================
def _hash_text(text: str) -> str:
    try:
        t = " ".join(text.strip().lower().split())
        return hashlib.md5(t.encode("utf-8")).hexdigest()
    except Exception:
        return ""


# ================= DEDUP =================
def deduplicate(docs: List[Document]) -> List[Document]:
    seen = set()
    out: List[Document] = []

    for d in docs:
        try:
            if not isinstance(d, Document):
                continue

            text = getattr(d, "page_content", "")
            if not text:
                continue

            h = _hash_text(text)
            if h in seen:
                continue

            seen.add(h)
            out.append(d)

        except Exception:
            continue

    return out


# ================= TOKEN ESTIMATE =================
def _approx_tokens(text: str) -> int:
    try:
        return max(1, int(len(text.split()) / 0.75))
    except Exception:
        return 1


# ================= CONTEXT BUILDER =================
def build_context(
    docs: List[Document],
    cfg: ContextConfig,
) -> Tuple[str, List[Dict[str, Any]]]:

    context_parts: List[str] = []
    sources: List[Dict[str, Any]] = []
    used = 0

    try:
        if not docs:
            return "", []

        for i, d in enumerate(docs, start=1):
            try:
                if not isinstance(d, Document):
                    continue

                content = getattr(d, "page_content", "")
                if not content:
                    continue

                md = d.metadata or {}

                src = md.get("source", "unknown")
                page = md.get("page", None)
                year = md.get("year", None)
                doc_type = md.get("type", None)
                tags = md.get("tags", [])

                header = ""
                if cfg.include_metadata_header:
                    header = (
                        f"[{i}] source={src} | page={page} | "
                        f"year={year} | type={doc_type} | tags={tags}\n"
                    )

                MAX_CHARS = 400

                body_full = content.strip()
                body_preview = body_full[:MAX_CHARS] + (
                    "..." if len(body_full) > MAX_CHARS else ""
                )

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

            except Exception as e:
                print("Block error:", e)
                continue

    except Exception as e:
        print("Context build error:", e)

    # 🔥 ALWAYS SAFE RETURN
    context_text = "\n---\n".join(context_parts).strip()

    return context_text, sources


# ================= CLI =================
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Context Builder Runner")
    p.add_argument("--query", type=str, default=None)
    p.add_argument("--top_k", type=int, default=5)
    p.add_argument("--year", type=str, default=None)
    p.add_argument("--type", dest="doc_type", type=str, default=None)
    p.add_argument("--max_context_tokens", type=int, default=1800)
    p.add_argument("--no_headers", action="store_true")
    return p.parse_args()


# ================= RUN =================
def run_once(query: str, cfg: ContextConfig) -> None:
    try:
        filters: Dict[str, Any] = {}

        if cfg.year:
            filters["year"] = cfg.year
        if cfg.doc_type:
            filters["type"] = cfg.doc_type

        retriever = HybridRetriever()
        candidates = retriever.retrieve_candidates(
            query, top_k=cfg.top_k, filters=filters
        )

        if not candidates:
            print("No chunks matched filters.")
            return

        reranker = Reranker()
        reranked = reranker.rerank(query, candidates, top_k=cfg.top_k)

        final_docs = _safe_docs(reranked)

        if not final_docs:
            print("No valid documents after reranking.")
            return

        final_docs = deduplicate(final_docs)

        context_text, sources = build_context(final_docs, cfg)

        print("\n===== FINAL CONTEXT =====\n")
        print(context_text if context_text else "(Empty)")

        print("\n===== SOURCES =====")
        for s in sources:
            print(f"{s['rank']}. {s['source']} (page {s['page']})")

    except Exception as e:
        print("Run error:", e)


# ================= MAIN =================
def main():
    args = parse_args()

    cfg = ContextConfig(
        top_k=args.top_k,
        year=args.year,
        doc_type=args.doc_type,
        max_context_tokens=args.max_context_tokens,
        include_metadata_header=not args.no_headers,
    )

    if not args.query:
        print("\n=== Context Builder ===\n")
        try:
            while True:
                q = input("Query> ").strip()
                if q:
                    run_once(q, cfg)
        except KeyboardInterrupt:
            print("\nExit\n")
        return

    run_once(args.query, cfg)


if __name__ == "__main__":
    main()