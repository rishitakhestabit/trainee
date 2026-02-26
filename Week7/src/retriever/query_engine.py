from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from src.embeddings.embedder import EmbedderConfig, LocalEmbedder

VECTORSTORE_DIR = Path("src/vectorstore")


@dataclass
class QueryConfig:
    top_k: int = 5
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"


class QueryEngine:
    def __init__(self, cfg: Optional[QueryConfig] = None, vectorstore_dir: Path = VECTORSTORE_DIR):
        self.cfg = cfg or QueryConfig()
        self.embedder = LocalEmbedder(EmbedderConfig(model_name=self.cfg.embedding_model_name))
        self.vs = FAISS.load_local(
            str(vectorstore_dir),
            self.embedder.langchain_embeddings,
            allow_dangerous_deserialization=True,
        )

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Document]:
        k = top_k if top_k is not None else self.cfg.top_k
        return self.vs.similarity_search(query, k=k)

    @staticmethod
    def pretty_print(docs: List[Document]) -> None:
        for i, d in enumerate(docs, start=1):
            src = d.metadata.get("source", "unknown")
            page = d.metadata.get("page", None)
            tags = d.metadata.get("tags", [])
            print("\n" + "=" * 80)
            print(f"[{i}] source={src} | page={page} | tags={tags}")
            print("-" * 80)
            print(d.page_content[:1200] + ("..." if len(d.page_content) > 1200 else ""))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--top_k", type=int, default=5)
    parser.add_argument("--embedding_model", type=str, default="sentence-transformers/all-MiniLM-L6-v2")
    return parser.parse_args()


def interactive_loop(engine: QueryEngine, top_k: int):
    print("\n Interactive Query Mode")
    print("Type your query and press Enter.")
    print("Press Ctrl+C to exit.\n")

    try:
        while True:
            q = input("Query> ").strip()
            if not q:
                continue

            docs = engine.retrieve(q, top_k=top_k)
            engine.pretty_print(docs)

    except KeyboardInterrupt:
        print("\n Exiting")


def main():
    args = parse_args()

    engine = QueryEngine(
        QueryConfig(top_k=args.top_k, embedding_model_name=args.embedding_model)
    )

    interactive_loop(engine, top_k=args.top_k)


if __name__ == "__main__":
    main()