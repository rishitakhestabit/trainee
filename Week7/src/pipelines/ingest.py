from pathlib import Path
from src.utils.doc_loaders import load_any
from src.utils.chunking import make_chunks
from src.embeddings.embedder import Embedder
from src.vectorstore.faiss_store import FaissVectorStore, FaissPaths
import json


RAW_DIR = Path("src/data/raw")
CHUNK_PATH = Path("src/data/chunks/chunks.json")
INDEX_PATH = Path("src/data/vectorstore/index.faiss")
META_PATH = Path("src/data/vectorstore/index_meta.json")


def discover_files():
    return [p for p in RAW_DIR.rglob("*") if p.suffix.lower() in [".pdf",".txt",".docx",".csv",".md"]]


def ingest():
    files = discover_files()
    print("Files:", files)

    docs = []
    for f in files:
        docs.extend(load_any(f))

    chunks = make_chunks(docs, tags=["week7","rag"])

    CHUNK_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHUNK_PATH.write_text(json.dumps(chunks, indent=2))

    embedder = Embedder()
    embeddings = embedder.embed_texts([c["text"] for c in chunks])

    store = FaissVectorStore(FaissPaths(INDEX_PATH, META_PATH))
    store.build(embeddings, chunks)
    store.save()

    print("DONE → index created")


if __name__ == "__main__":
    ingest()