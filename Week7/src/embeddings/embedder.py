from dataclasses import dataclass
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


@dataclass
class EmbedderConfig:
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    normalize: bool = True


class Embedder:
    def __init__(self, config: EmbedderConfig = EmbedderConfig()):
        self.model = SentenceTransformer(config.model_name)
        self.normalize = config.normalize

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True,
            normalize_embeddings=self.normalize
        )
        return embeddings.astype("float32")

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed_texts([query])[0]