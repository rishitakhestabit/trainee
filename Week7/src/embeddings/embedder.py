from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from langchain_community.embeddings import HuggingFaceEmbeddings


@dataclass
class EmbedderConfig:
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    normalize_embeddings: bool = True


class LocalEmbedder:
    """
    Local embeddings using LangChain's HuggingFaceEmbeddings.
    """

    def __init__(self, cfg: Optional[EmbedderConfig] = None):
        self.cfg = cfg or EmbedderConfig()
        self._emb = HuggingFaceEmbeddings(
            model_name=self.cfg.model_name,
            encode_kwargs={"normalize_embeddings": self.cfg.normalize_embeddings},
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._emb.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._emb.embed_query(text)

    @property
    def langchain_embeddings(self) -> HuggingFaceEmbeddings:
        return self._emb