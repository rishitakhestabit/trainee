from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from src.embeddings.embedder import EmbedderConfig, LocalEmbedder


# ------------------ DEFAULT PROJECT PATHS ------------------
RAW_DIR = Path("src/data/raw")
CLEANED_DIR = Path("src/data/cleaned")
CHUNKS_DIR = Path("src/data/chunks")
VECTORSTORE_DIR = Path("src/vectorstore")  # index.faiss + index.pkl

for p in [RAW_DIR, CLEANED_DIR, CHUNKS_DIR, VECTORSTORE_DIR]:
    p.mkdir(parents=True, exist_ok=True)


# ------------------ CONFIG ------------------
@dataclass
class IngestConfig:
    tags: List[str]
    chunk_min_tokens: int = 500
    chunk_max_tokens: int = 800
    chunk_overlap_tokens: int = 80
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"


# ------------------ TOKEN LENGTH FUNCTION ------------------
def _get_hf_tokenizer(model_name: str):
    try:
        from transformers import AutoTokenizer  # type: ignore
        return AutoTokenizer.from_pretrained(model_name, use_fast=True)
    except Exception:
        return None


def _token_length_fn_factory(model_name: str):
    tok = _get_hf_tokenizer(model_name)

    if tok is None:
        # fallback approximate token count
        def length_fn(text: str) -> int:
            return max(1, int(len(text.split()) / 0.75))

        return length_fn

    def length_fn(text: str) -> int:
        return len(tok.encode(text, add_special_tokens=False))

    return length_fn


# ------------------ CLEANING ------------------
_whitespace_re = re.compile(r"\s+")


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = _whitespace_re.sub(" ", text)
    return text.strip()


# ------------------ LOADERS ------------------
def _load_one_file(path: Path) -> List[Document]:
    ext = path.suffix.lower()

    if ext == ".pdf":
        return PyPDFLoader(str(path)).load()

    if ext in [".txt", ".md"]:
        return TextLoader(str(path), encoding="utf-8").load()

    if ext == ".csv":
        return CSVLoader(str(path), encoding="utf-8").load()

    if ext in [".docx", ".doc"]:
        return UnstructuredWordDocumentLoader(str(path)).load()

    return []


def load_documents(raw_dir: Path) -> List[Document]:
    docs: List[Document] = []
    for fp in raw_dir.rglob("*"):
        if fp.is_file() and fp.suffix.lower() in {".pdf", ".txt", ".md", ".csv", ".docx", ".doc"}:
            docs.extend(_load_one_file(fp))
    return docs


# ------------------ METADATA HELPERS (NEW FOR DAY 2 FILTERS) ------------------
def _infer_year_from_source(source: str) -> Optional[str]:
    m = re.search(r"(19|20)\d{2}", source)
    return m.group(0) if m else None


def _infer_type_from_source(source: str, tags: List[str]) -> Optional[str]:
    
    s = source.lower()
    joined_tags = " ".join([t.lower() for t in tags])

    candidates = ["policy", "report", "manual", "contract", "guideline", "sop", "invoice", "presentation"]
    for c in candidates:
        if c in s or c in joined_tags:
            return c
    return None


def _merge_tags(existing: Any, default_tags: List[str]) -> List[str]:
    if isinstance(existing, list):
        base = [str(t) for t in existing]
    elif isinstance(existing, str):
        base = [t.strip() for t in existing.split(",") if t.strip()]
    else:
        base = []

    # ensure defaults included
    for t in default_tags:
        if t not in base:
            base.append(t)

    # remove duplicates while preserving order
    seen = set()
    out: List[str] = []
    for t in base:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


# ------------------ METADATA (UPDATED) ------------------
def enrich_metadata(docs: Iterable[Document], default_tags: List[str]) -> List[Document]:
    """
    Day 1 required:
      - source
      - page
      - tags

    Day 2 requires filters like:
      filters = {"year":"2024", "type":"policy"}

    So we also ensure:
      - year
      - type
    """
    out: List[Document] = []
    for d in docs:
        src = d.metadata.get("source") or d.metadata.get("file_path") or "unknown"
        page = d.metadata.get("page")  # can be None

        tags = _merge_tags(d.metadata.get("tags"), default_tags)

        year = d.metadata.get("year") or _infer_year_from_source(str(src))
        doc_type = d.metadata.get("type") or _infer_type_from_source(str(src), tags)

        out.append(
            Document(
                page_content=d.page_content,
                metadata={
                    **d.metadata,
                    "source": src,
                    "page": page,
                    "tags": tags,
                    "year": year,
                    "type": doc_type,
                },
            )
        )
    return out


# ------------------ CHUNKING ------------------
def chunk_documents(docs: List[Document], cfg: IngestConfig) -> List[Document]:
    length_fn = _token_length_fn_factory(cfg.embedding_model_name)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=cfg.chunk_max_tokens,
        chunk_overlap=cfg.chunk_overlap_tokens,
        length_function=length_fn,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    cleaned_docs: List[Document] = [Document(page_content=clean_text(d.page_content), metadata=d.metadata) for d in docs]

    chunks = splitter.split_documents(cleaned_docs)

    filtered: List[Document] = []
    for c in chunks:
        if length_fn(c.page_content) >= cfg.chunk_min_tokens:
            filtered.append(c)

    return filtered


# ------------------ SAVE CHUNKS ------------------
def save_chunks_jsonl(chunks: List[Document], out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8") as f:
        for i, d in enumerate(chunks):
            f.write(
                json.dumps(
                    {"id": i, "text": d.page_content, "metadata": d.metadata},
                    ensure_ascii=False,
                )
                + "\n"
            )


# ------------------ FAISS BUILD ------------------
def build_faiss(chunks: List[Document], embedder: LocalEmbedder, out_dir: Path) -> None:
    vs = FAISS.from_documents(chunks, embedder.langchain_embeddings)
    vs.save_local(str(out_dir))


# ------------------ CLI (OPTIONAL) ------------------
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw_dir", type=str, default=None)
    parser.add_argument("--tags", type=str, default=None)
    parser.add_argument("--embedding_model", type=str, default=None)
    return parser.parse_args()


def main():
    args = parse_args()

    # Defaults so you can run: python -m src.pipelines.ingest
    raw_dir = Path(args.raw_dir) if args.raw_dir else RAW_DIR
    tags_str = args.tags if args.tags else "week7,text-rag"
    embedding_model = args.embedding_model if args.embedding_model else "sentence-transformers/all-MiniLM-L6-v2"

    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    cfg = IngestConfig(tags=tags, embedding_model_name=embedding_model)

    print(f"[INGEST] raw_dir={raw_dir}")
    print(f"[INGEST] tags={cfg.tags}")
    print(f"[INGEST] embedding_model={cfg.embedding_model_name}")

    docs = load_documents(raw_dir)
    print(f"[INGEST] Loaded docs: {len(docs)}")

    docs = enrich_metadata(docs, default_tags=cfg.tags)
    print("[INGEST] Metadata ensured: source/page/tags/year/type")

    chunks = chunk_documents(docs, cfg)
    print(f"[INGEST] Chunks created (filtered): {len(chunks)}")

    chunks_path = CHUNKS_DIR / "chunks.jsonl"
    save_chunks_jsonl(chunks, chunks_path)
    print(f"[INGEST] Saved chunks: {chunks_path}")

    embedder = LocalEmbedder(EmbedderConfig(model_name=cfg.embedding_model_name, normalize_embeddings=True))
    build_faiss(chunks, embedder, VECTORSTORE_DIR)
    print(f"[INGEST] Saved FAISS: {VECTORSTORE_DIR}/index.faiss + index.pkl")

    print("[INGEST] Day-1 updated: now supports Day-2 filters (year/type).")


if __name__ == "__main__":
    main()