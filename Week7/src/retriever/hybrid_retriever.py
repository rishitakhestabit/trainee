# src/retriever/hybrid_retriever.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
import json
import re

from rank_bm25 import BM25Okapi

from src.embeddings.embedder import Embedder
from src.vectorstore.faiss_store import FaissVectorStore, FaissPaths
from src.retriever.reranker import CosineReranker, RerankConfig


INDEX_PATH = Path("src/data/vectorstore/index.faiss")
META_PATH = Path("src/data/vectorstore/index_meta.json")


@dataclass
class HybridConfig:
    # pull more candidates, then refine down
    semantic_k: int = 30
    keyword_k: int = 30
    rerank_top_n: int = 30

    # final output size controlled by retrieve(top_k=...)
    use_keyword_fallback: bool = True
    enable_dedup: bool = True
    enable_mmr: bool = True
    mmr_lambda: float = 0.7
    enable_rerank: bool = True


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _norm(text: str) -> str:
    text = text.lower().strip()
    return re.sub(r"\s+", " ", text)


def _passes_filters(meta: Dict[str, Any], filters: Optional[Dict[str, Any]]) -> bool:
    """
    Supported filters:
      - exact meta match: {"type":"pdf"}  (works with your current meta)
      - source_contains: {"source_contains":"astrazeneca"}
      - tag: {"tag":"rag"}
      - any other meta key if present
    """
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


def _dedup(cands: List[Tuple[float, Dict[str, Any]]]) -> List[Tuple[float, Dict[str, Any]]]:
    """
    Deduplicate by normalized text prefix.
    Keep the best scoring candidate per unique text.
    """
    best: Dict[str, Tuple[float, Dict[str, Any]]] = {}
    for score, item in cands:
        text = item.get("text", "")
        if not text.strip():
            continue
        key = _norm(text[:800])
        if key not in best or score > best[key][0]:
            best[key] = (score, item)

    out = list(best.values())
    out.sort(key=lambda x: x[0], reverse=True)
    return out


def _mmr_select(
    query: str,
    candidates: List[Tuple[float, Dict[str, Any]]],
    embedder: Embedder,
    top_k: int,
    lam: float,
) -> List[Tuple[float, Dict[str, Any]]]:
    """
    Max Marginal Relevance: pick relevant chunks that are not too similar to each other.
    """
    if not candidates:
        return []

    texts = [it["text"] for _, it in candidates]
    q_vec = embedder.embed_query(query)
    doc_vecs = embedder.embed_texts(texts)

    rel = (doc_vecs @ q_vec).tolist()     # relevance to query
    sim = (doc_vecs @ doc_vecs.T)         # doc-doc similarity

    selected: List[int] = []
    remaining = list(range(len(candidates)))

    while remaining and len(selected) < top_k:
        best_i = None
        best_score = -1e9

        for i in remaining:
            if not selected:
                mmr = rel[i]
            else:
                max_sim = max(float(sim[i, j]) for j in selected)
                mmr = lam * rel[i] - (1 - lam) * max_sim

            if mmr > best_score:
                best_score = mmr
                best_i = i

        selected.append(best_i)
        remaining.remove(best_i)

    return [candidates[i] for i in selected]


class HybridRetriever:
    """
    Day-2: Hybrid Retrieval (BM25 + FAISS) + Reranking + Dedup + MMR + Filters
    """

    def __init__(
        self,
        index_path: Path = INDEX_PATH,
        meta_path: Path = META_PATH,
        config: HybridConfig = HybridConfig(),
    ):
        self.config = config
        self.embedder = Embedder()

        # Semantic store
        self.store = FaissVectorStore(FaissPaths(index_path, meta_path))
        self.store.load()

        # Metadata + BM25 corpus
        self.items: List[Dict[str, Any]] = json.loads(meta_path.read_text(encoding="utf-8"))
        self.bm25 = BM25Okapi([_tokenize(x["text"]) for x in self.items])

        # Reranker
        self.reranker = CosineReranker(self.embedder, RerankConfig())

    def semantic_search(self, query: str, k: int, filters: Optional[Dict[str, Any]]) -> List[Tuple[float, Dict[str, Any]]]:
        q_vec = self.embedder.embed_query(query)
        hits = self.store.search(q_vec, k=k)  # IMPORTANT: your FAISS wrapper uses k=
        if filters:
            hits = [(s, it) for (s, it) in hits if _passes_filters(it.get("meta", {}), filters)]
        return hits

    def keyword_search(self, query: str, k: int, filters: Optional[Dict[str, Any]]) -> List[Tuple[float, Dict[str, Any]]]:
        q_tokens = _tokenize(query)
        scores = self.bm25.get_scores(q_tokens)

        idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        out: List[Tuple[float, Dict[str, Any]]] = []
        for i in idxs:
            item = self.items[i]
            if filters and not _passes_filters(item.get("meta", {}), filters):
                continue
            out.append((float(scores[i]), item))
        return out

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[float, Dict[str, Any]]]:
        sem = self.semantic_search(query, k=self.config.semantic_k, filters=filters)
        kw = self.keyword_search(query, k=self.config.keyword_k, filters=filters)

        candidates = sem + kw
        if self.config.use_keyword_fallback and not sem:
            candidates = kw

        if self.config.enable_dedup:
            candidates = _dedup(candidates)

        if self.config.enable_rerank:
            candidates = self.reranker.rerank(query, candidates, top_k=self.config.rerank_top_n)
        else:
            candidates.sort(key=lambda x: x[0], reverse=True)

        if self.config.enable_mmr:
            candidates = _mmr_select(query, candidates, self.embedder, top_k=top_k, lam=self.config.mmr_lambda)
        else:
            candidates = candidates[:top_k]

        return candidates