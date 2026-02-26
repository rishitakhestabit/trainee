from __future__ import annotations

import json
import re
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from src.embeddings.embedder import EmbedderConfig, LocalEmbedder

# pip install rank_bm25
from rank_bm25 import BM25Okapi


CHUNKS_JSONL = Path("src/data/chunks/chunks.jsonl")
VECTORSTORE_DIR = Path("src/vectorstore")


def _simple_tokenize(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    return [t for t in text.split() if t]


def _text_hash(text: str) -> str:
    t = " ".join(text.strip().lower().split())
    return hashlib.md5(t.encode("utf-8")).hexdigest()


def _doc_key(d: Document) -> str:
    src = str(d.metadata.get("source", "unknown"))
    page = str(d.metadata.get("page", ""))
    h = _text_hash(d.page_content)
    return f"{src}::p{page}::{h}"


def _normalize_scores(items: List[Tuple[str, float]]) -> Dict[str, float]:
    if not items:
        return {}
    vals = [s for _, s in items]
    mn, mx = min(vals), max(vals)
    if mx == mn:
        return {k: 1.0 for k, _ in items}
    return {k: (s - mn) / (mx - mn) for k, s in items}


def _distance_to_similarity(dist: float) -> float:
    # Convert FAISS distance to a bounded similarity score
    return 1.0 / (1.0 + float(dist))


def _infer_year_from_source(source: str) -> Optional[str]:
    m = re.search(r"(19|20)\d{2}", source)
    return m.group(0) if m else None


def _passes_filters(d: Document, filters: Optional[Dict[str, Any]]) -> bool:
    """
    Supports Day-2 filters:
      filters = {"year":"2024", "type":"policy"}

    Uses metadata if present; safe fallback if missing:
    - year inferred from source filename/path containing YYYY
    - type inferred from tags or source path containing the type string
    """
    if not filters:
        return True

    md = d.metadata or {}
    src = str(md.get("source", "")).lower()
    tags = md.get("tags", [])
    tags_str = " ".join([str(t).lower() for t in tags]) if isinstance(tags, list) else str(tags).lower()

    for k, v in filters.items():
        if v is None:
            continue
        v_str = str(v).lower()

        if k.lower() == "year":
            year_val = md.get("year")
            year_val = str(year_val).lower() if year_val is not None else (str(_infer_year_from_source(src) or "").lower())
            if year_val != v_str:
                return False

        elif k.lower() == "type":
            type_val = md.get("type")
            type_val = str(type_val).lower() if type_val is not None else ""
            if not type_val:
                # fallback
                if v_str in tags_str or v_str in src:
                    type_val = v_str
            if type_val != v_str:
                return False

        else:
            # generic exact match
            val = md.get(k)
            if val is None or str(val).lower() != v_str:
                return False

    return True


def _cosine(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _mmr_select(
    query_vec: List[float],
    cand_vecs: List[List[float]],
    cand_keys: List[str],
    k: int,
    lambda_mult: float,
) -> List[str]:
    """
    MMR (Max Marginal Relevance):
    select docs that are relevant to query AND diverse across each other.
    """
    if k <= 0 or not cand_vecs:
        return []

    selected: List[int] = []
    remaining = list(range(len(cand_vecs)))
    sim_to_q = [_cosine(query_vec, v) for v in cand_vecs]

    while remaining and len(selected) < k:
        if not selected:
            best = max(remaining, key=lambda i: sim_to_q[i])
            selected.append(best)
            remaining.remove(best)
            continue

        def mmr_score(i: int) -> float:
            rel = sim_to_q[i]
            red = max(_cosine(cand_vecs[i], cand_vecs[j]) for j in selected)
            return lambda_mult * rel - (1.0 - lambda_mult) * red

        best = max(remaining, key=mmr_score)
        selected.append(best)
        remaining.remove(best)

    return [cand_keys[i] for i in selected]


@dataclass
class HybridRetrieverConfig:
    # final top_k is applied after rerank; here we mainly produce candidates
    top_k: int = 5

    # hybrid weighting between vector vs bm25
    alpha: float = 0.6

    # candidate pool size = top_k * multiplier
    candidate_multiplier: int = 8

    # MMR diversity on candidate pool
    use_mmr: bool = True
    mmr_lambda: float = 0.6

    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"


class HybridRetriever:
    """
    Day-2:
    - Hybrid retrieval (FAISS + BM25)
    - Filters
    - MMR diversity on candidates
    Returns candidates for reranking.
    """

    def __init__(
        self,
        cfg: Optional[HybridRetrieverConfig] = None,
        vectorstore_dir: Path = VECTORSTORE_DIR,
        chunks_jsonl: Path = CHUNKS_JSONL,
    ):
        self.cfg = cfg or HybridRetrieverConfig()

        # embeddings + FAISS
        self.embedder = LocalEmbedder(EmbedderConfig(model_name=self.cfg.embedding_model_name))
        self.vs = FAISS.load_local(
            str(vectorstore_dir),
            self.embedder.langchain_embeddings,
            allow_dangerous_deserialization=True,
        )

        # BM25 corpus from chunks.jsonl (Day-1 output)
        if not chunks_jsonl.exists():
            raise FileNotFoundError(f"Missing {chunks_jsonl}. Run: python -m src.pipelines.ingest")

        self.corpus_docs: List[Document] = []
        corpus_tokens: List[List[str]] = []

        with chunks_jsonl.open("r", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                md = rec.get("metadata", {}) or {}
                self.corpus_docs.append(Document(page_content=rec["text"], metadata=md))
                corpus_tokens.append(_simple_tokenize(rec["text"]))

        self.bm25 = BM25Okapi(corpus_tokens)

    def retrieve_candidates(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Returns a candidate list (larger than top_k) after hybrid merge + optional MMR.
        This is intentionally a "candidate stage" before cross-encoder reranking.
        """
        cand_n = max(1, top_k * self.cfg.candidate_multiplier)

        # 1) Vector candidates (semantic)
        vec_pairs = self.vs.similarity_search_with_score(query, k=cand_n)
        vec = [(d, _distance_to_similarity(dist)) for d, dist in vec_pairs if _passes_filters(d, filters)]

        # 2) BM25 candidates (keyword fallback)
        scores = self.bm25.get_scores(_simple_tokenize(query))
        kw = [(d, float(s)) for d, s in zip(self.corpus_docs, scores) if _passes_filters(d, filters)]
        kw.sort(key=lambda x: x[1], reverse=True)
        kw = kw[:cand_n]

        # 3) Normalize and merge
        vec_norm = _normalize_scores([(_doc_key(d), s) for d, s in vec])
        kw_norm = _normalize_scores([(_doc_key(d), s) for d, s in kw])

        merged: Dict[str, Dict[str, Any]] = {}

        def ensure(key: str, d: Document):
            if key not in merged:
                merged[key] = {"doc": d, "vec": 0.0, "bm25": 0.0}

        for d, _ in vec:
            key = _doc_key(d)
            ensure(key, d)
            merged[key]["vec"] = vec_norm.get(key, 0.0)

        for d, _ in kw:
            key = _doc_key(d)
            ensure(key, d)
            merged[key]["bm25"] = kw_norm.get(key, 0.0)

        scored: List[Tuple[Document, float, str]] = []
        for key, obj in merged.items():
            v = float(obj["vec"])
            b = float(obj["bm25"])
            hybrid = self.cfg.alpha * v + (1.0 - self.cfg.alpha) * b
            scored.append((obj["doc"], hybrid, key))

        scored.sort(key=lambda x: x[1], reverse=True)

        # 4) Optional MMR to diversify candidate pool
        if self.cfg.use_mmr and scored:
            # take a manageable slice for MMR embedding compute
            pre = scored[:cand_n]
            cand_docs = [d for d, _, _ in pre]
            cand_keys = [k for _, _, k in pre]
            query_vec = self.embedder.embed_query(query)
            cand_vecs = self.embedder.embed_documents([d.page_content for d in cand_docs])

            selected_keys = _mmr_select(
                query_vec=query_vec,
                cand_vecs=cand_vecs,
                cand_keys=cand_keys,
                k=min(cand_n, len(cand_docs)),
                lambda_mult=self.cfg.mmr_lambda,
            )

            key_to_doc = {k: d for d, _, k in pre}
            return [key_to_doc[k] for k in selected_keys if k in key_to_doc]

        return [d for d, _, _ in scored[:cand_n]]