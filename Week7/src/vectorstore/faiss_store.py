from dataclasses import dataclass
from pathlib import Path
import json
import faiss
import numpy as np


@dataclass
class FaissPaths:
    index_path: Path
    meta_path: Path


class FaissVectorStore:
    def __init__(self, paths: FaissPaths):
        self.paths = paths
        self.index = None
        self.meta = []

    def build(self, embeddings: np.ndarray, metadata):
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings.astype("float32"))
        self.meta = metadata

    def save(self):
        self.paths.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.paths.index_path))
        self.paths.meta_path.write_text(json.dumps(self.meta, indent=2))

    def load(self):
        self.index = faiss.read_index(str(self.paths.index_path))
        self.meta = json.loads(self.paths.meta_path.read_text())

    def search(self, query_vec, k=5):
        D, I = self.index.search(query_vec.reshape(1, -1).astype("float32"), k)
        return [(float(score), self.meta[idx]) for score, idx in zip(D[0], I[0])]