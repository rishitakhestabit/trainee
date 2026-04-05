from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

from langchain_core.documents import Document

from sentence_transformers import CrossEncoder

from src.embeddings.embedder import EmbedderConfig, LocalEmbedder


@dataclass
class RerankerConfig:
    cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"


class Reranker:
    """
    Production-safe reranker:
    - CrossEncoder primary
    - Embedding fallback
    - Handles mixed inputs safely
    """

    def __init__(self, cfg: Optional[RerankerConfig] = None):
        try:
            self.cfg = cfg or RerankerConfig()
        except Exception as e:
            print("Config error:", e)
            self.cfg = RerankerConfig()

        # -------- Cross Encoder --------
        try:
            self._ce: Optional[CrossEncoder] = CrossEncoder(self.cfg.cross_encoder_model)
        except Exception as e:
            print("CrossEncoder load failed:", e)
            self._ce = None

        # -------- Embedder --------
        try:
            self._embedder = LocalEmbedder(
                EmbedderConfig(model_name=self.cfg.embedding_model_name)
            )
        except Exception as e:
            print("Embedder init failed:", e)
            self._embedder = None

    # ================= NORMALIZATION =================
    def _normalize_docs(
        self, docs: List[Union[Document, Tuple[Document, float]]]
    ) -> List[Document]:
        try:
            normalized = []
            for d in docs:
                if isinstance(d, tuple):
                    normalized.append(d[0])
                else:
                    normalized.append(d)
            return normalized
        except Exception as e:
            print("Normalization error:", e)
            return []

    # ================= RERANK =================
    def rerank(
        self,
        query: str,
        docs: List[Union[Document, Tuple[Document, float]]],
        top_k: int
    ) -> List[Tuple[Document, float]]:

        try:
            if not docs:
                return []

            # -------- Normalize --------
            docs = self._normalize_docs(docs)

            if not docs:
                return []

            # ================= CROSS ENCODER =================
            if self._ce is not None:
                try:
                    pairs = [(query, d.page_content) for d in docs]
                    scores = self._ce.predict(pairs)

                    ranked = list(zip(docs, [float(s) for s in scores]))
                    ranked.sort(key=lambda x: x[1], reverse=True)

                    return ranked[:top_k]

                except Exception as e:
                    print("CrossEncoder failed:", e)

            # ================= FALLBACK =================
            try:
                if self._embedder is None:
                    raise ValueError("Embedder not initialized")

                qv = self._embedder.embed_query(query)
                dvs = self._embedder.embed_documents([d.page_content for d in docs])

                def dot(a, b):
                    try:
                        return float(sum(x * y for x, y in zip(a, b)))
                    except Exception:
                        return 0.0

                ranked = [(d, dot(qv, v)) for d, v in zip(docs, dvs)]
                ranked.sort(key=lambda x: x[1], reverse=True)

                return ranked[:top_k]

            except Exception as e:
                print("Fallback failed:", e)

                # -------- FINAL SAFETY --------
                return [(d, 0.0) for d in docs[:top_k]]

        except Exception as e:
            print("Rerank completely failed:", e)

            # -------- HARD FAIL SAFE --------
            return [(d, 0.0) for d in docs[:top_k] if isinstance(d, Document)]