from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from langchain_core.documents import Document

# pip install sentence-transformers
from sentence_transformers import CrossEncoder

from src.embeddings.embedder import EmbedderConfig, LocalEmbedder


@dataclass
class RerankerConfig:
    cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"  # used only for fallback


class Reranker:
    """
    Day-2 reranking:
    - Primary: cross-encoder rerank
    - Fallback: cosine similarity using embeddings (if cross-encoder fails)
    """

    def __init__(self, cfg: Optional[RerankerConfig] = None):
        self.cfg = cfg or RerankerConfig()

        self._ce: Optional[CrossEncoder] = None
        try:
            self._ce = CrossEncoder(self.cfg.cross_encoder_model)
        except Exception:
            self._ce = None

        # for cosine fallback
        self._embedder = LocalEmbedder(EmbedderConfig(model_name=self.cfg.embedding_model_name))

    def rerank(self, query: str, docs: List[Document], top_k: int) -> List[Tuple[Document, float]]:
        if not docs:
            return []

        if self._ce is not None:
            pairs = [(query, d.page_content) for d in docs]
            scores = self._ce.predict(pairs)
            ranked = list(zip(docs, [float(s) for s in scores]))
            ranked.sort(key=lambda x: x[1], reverse=True)
            return ranked[:top_k]

        # ----- cosine fallback -----
        qv = self._embedder.embed_query(query)
        dvs = self._embedder.embed_documents([d.page_content for d in docs])

        def dot(a, b):
            return float(sum(x * y for x, y in zip(a, b)))

        ranked = [(d, dot(qv, v)) for d, v in zip(docs, dvs)]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:top_k]