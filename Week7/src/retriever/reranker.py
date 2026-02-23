# src/retriever/reranker.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from src.embeddings.embedder import Embedder


@dataclass
class RerankConfig:
    """
    weight_retrieval_score: keeps some signal from original retrieval (FAISS/BM25 score)
    """
    weight_retrieval_score: float = 0.20


class CosineReranker:
    """
    Rerank by cosine similarity between query and candidate chunk embeddings.
    Works best if Embedder returns normalized embeddings.
    """

    def __init__(self, embedder: Embedder, config: RerankConfig = RerankConfig()):
        self.embedder = embedder
        self.config = config

    def rerank(
        self,
        query: str,
        candidates: List[Tuple[float, Dict[str, Any]]],
        top_k: int = 20,
    ) -> List[Tuple[float, Dict[str, Any]]]:
        if not candidates:
            return []

        texts = [item["text"] for _, item in candidates]
        q_vec = self.embedder.embed_query(query).astype("float32")
        doc_vecs = self.embedder.embed_texts(texts).astype("float32")

        # dot product == cosine similarity if embeddings are normalized
        sims = doc_vecs @ q_vec  # (n,)

        reranked: List[Tuple[float, Dict[str, Any]]] = []
        w = self.config.weight_retrieval_score

        for (base_score, item), sim in zip(candidates, sims):
            final_score = (1 - w) * float(sim) + w * float(base_score)
            reranked.append((final_score, item))

        reranked.sort(key=lambda x: x[0], reverse=True)
        return reranked[:top_k]