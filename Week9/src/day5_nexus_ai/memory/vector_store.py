import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
from pathlib import Path
from config import BASE_DIR


class VectorStore:

    def __init__(self, dim=768, index_path="memory/faiss.index", model_name=None):

        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
        self.allow_download = os.getenv("EMBEDDINGS_ALLOW_DOWNLOAD", "0") != "0"
        self.model = None
        self.model_error = None
        path = Path(index_path)
        if not path.is_absolute():
            path = BASE_DIR / path

        self.index_path = str(path)
        self.dim = dim

        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            base_index = faiss.IndexFlatIP(dim)
            self.index = faiss.IndexIDMap(base_index)


    def _get_model(self):

        if self.model is not None:
            return self.model

        if self.model_error is not None:
            return None

        try:
            if self.allow_download:
                self.model = SentenceTransformer(self.model_name)
            else:
                self.model = SentenceTransformer(self.model_name, local_files_only=True)
        except Exception as e:
            self.model_error = str(e)
            return None

        return self.model


    def _embed_doc(self, text: str):

        model = self._get_model()
        if model is None:
            return None

        emb = model.encode(
            f"passage: {text}",
            normalize_embeddings=True
        )

        return np.array([emb]).astype("float32")


    def _embed_query(self, text: str):

        model = self._get_model()
        if model is None:
            return None

        emb = model.encode(
            f"query: {text}",
            normalize_embeddings=True
        )

        return np.array([emb]).astype("float32")


    def add_text(self, memory_id: int, text: str):

        emb = self._embed_doc(text)
        if emb is None:
            return

        self.index.add_with_ids(
            emb,
            np.array([memory_id], dtype="int64")
        )

        self._save_index()


    def search(self, query: str, k=5):

        if self.index.ntotal == 0:
            return []

        q_emb = self._embed_query(query)
        if q_emb is None:
            return []

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
