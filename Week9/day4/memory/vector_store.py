import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os


class VectorStore:

    def __init__(self, dim=768, index_path="memory/faiss.index"):

        self.model = SentenceTransformer("BAAI/bge-base-en-v1.5")
        self.index_path = index_path
        self.dim = dim

        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        else:
            base_index = faiss.IndexFlatIP(dim)
            self.index = faiss.IndexIDMap(base_index)

    def _embed_doc(self, text: str):

        emb = self.model.encode(
            f"passage: {text}",
            normalize_embeddings=True
        )
        return np.array([emb]).astype("float32")
    
    def _embed_query(self, text: str):
        emb = self.model.encode(
            f"query: {text}",
            normalize_embeddings=True
        )
        return np.array([emb]).astype("float32")
    
    def add_text(self, memory_id: int, text: str):
        emb = self._embed_doc(text)
        self.index.add_with_ids(
            emb,
            np.array([memory_id], dtype="int64")
        )
        self._save_index()

    def search(self, query: str, k=5):

        if self.index.ntotal == 0:
            return []
        q_emb = self._embed_query(query)
        scores, ids = self.index.search(q_emb, k)
        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx == -1:
                continue
            results.append((int(idx), float(score)))
        return results


    def delete(self, memory_id: int):
        self.index.remove_ids(
            np.array([memory_id], dtype="int64")
        )
        self._save_index()


    def _save_index(self):
        directory = os.path.dirname(self.index_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        faiss.write_index(self.index, self.index_path)