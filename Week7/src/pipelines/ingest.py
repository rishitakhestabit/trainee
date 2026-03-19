from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import time

from src.embeddings.embedder import EmbedderConfig, LocalEmbedder


# ================= PATHS =================
RAW_DIR = Path("src/data/raw")
CHUNKS_DIR = Path("src/data/chunks")
CHUNKS_JSONL = CHUNKS_DIR / "chunks.jsonl"
VECTORSTORE_DIR = Path("src/vectorstore")

for p in [RAW_DIR, CHUNKS_DIR, VECTORSTORE_DIR]:
    p.mkdir(parents=True, exist_ok=True)


# ================= CONFIG =================
@dataclass
class IngestConfig:
    tags: List[str]
    chunk_min_tokens: int = 30        # lowered from 200 — avoids filtering all chunks
    chunk_max_tokens: int = 500
    chunk_overlap_tokens: int = 50
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"


# ================= TOKENIZER =================
def _get_hf_tokenizer(model_name: str):
    try:
        from transformers import AutoTokenizer
        return AutoTokenizer.from_pretrained(model_name, use_fast=True)
    except Exception:
        return None


def _token_length_fn_factory(model_name: str):
    tok = _get_hf_tokenizer(model_name)
    if tok is None:
        return lambda text: max(1, int(len(text.split()) / 0.75))
    return lambda text: len(tok.encode(text, add_special_tokens=False))


# ================= CLEAN =================
_whitespace_re = re.compile(r"\s+")


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = _whitespace_re.sub(" ", text)
    return text.strip()


# ================= LOAD =================
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


# ================= METADATA =================
def enrich_metadata(
    docs: Iterable[Document],
    tags: List[str],
    file_path: str
) -> List[Document]:
    out = []
    # Always store ONLY bare filename — never full/relative path.
    # e.g. "Week-7-1766484412108.pdf" not "src/data/raw/Week-7-...pdf"
    filename = Path(file_path).name

    for d in docs:
        out.append(
            Document(
                page_content=d.page_content,
                metadata={
                    **d.metadata,
                    "source": filename,
                    "uploaded_at": time.time(),
                    "tags": tags,
                }
            )
        )
    return out


# ================= CHUNK =================
def chunk_documents(docs: List[Document], cfg: IngestConfig) -> List[Document]:
    length_fn = _token_length_fn_factory(cfg.embedding_model_name)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=cfg.chunk_max_tokens,
        chunk_overlap=cfg.chunk_overlap_tokens,
        length_function=length_fn,
    )

    cleaned = [
        Document(page_content=clean_text(d.page_content), metadata=d.metadata)
        for d in docs
        if clean_text(d.page_content)
    ]

    chunks = splitter.split_documents(cleaned)
    filtered = [c for c in chunks if length_fn(c.page_content) >= cfg.chunk_min_tokens]

    print(
        f"[ingest] pages={len(docs)} | cleaned={len(cleaned)} | "
        f"chunks={len(chunks)} | after_filter={len(filtered)}"
    )

    return filtered


# ================= CLEAN OLD JSONL ENTRIES =================
def _clean_chunks_jsonl() -> None:
    """
    ✅ FIX for old PDFs appearing in answers:
    Previous ingests saved source as full paths like:
        "data/Week-2-....pdf"
        "src/data/raw/astrazeneca_2022.pdf"
    These pollute BM25 retrieval so old irrelevant PDFs keep appearing.

    This rewrites chunks.jsonl keeping ONLY entries with bare filenames
    (no slashes). Called automatically at the start of every run_ingestion().
    Safe to call repeatedly — skips if nothing dirty found.
    """
    if not CHUNKS_JSONL.exists():
        return

    clean_lines = []
    dirty_count = 0

    with CHUNKS_JSONL.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                source = rec.get("metadata", {}).get("source", "")
                # Reject entries whose source contains any path separator
                if "/" not in source and "\\" not in source:
                    clean_lines.append(line)
                else:
                    dirty_count += 1
            except Exception:
                continue

    if dirty_count > 0:
        print(
            f"[ingest] Removed {dirty_count} old bad-path entries from chunks.jsonl"
        )
        with CHUNKS_JSONL.open("w", encoding="utf-8") as f:
            for line in clean_lines:
                f.write(line + "\n")
    else:
        print("[ingest] chunks.jsonl is clean — no dirty entries found")


# ================= SAVE CHUNKS JSONL =================
def save_chunks_jsonl(chunks: List[Document]) -> None:
    """
    Appends new chunks to chunks.jsonl incrementally.
    HybridRetriever reads this at startup to build its BM25 corpus.
    Without this, BM25 and FAISS go out of sync → causes retrieval errors.
    """
    CHUNKS_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with CHUNKS_JSONL.open("a", encoding="utf-8") as f:
        for chunk in chunks:
            record = {
                "text": chunk.page_content,
                "metadata": chunk.metadata,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ================= EMBEDDER (with torch meta fix) =================
def _make_embedder(model_name: str) -> LocalEmbedder:
    """
    Handles torch meta tensor error:
    'Cannot copy out of meta tensor; no data!'
    Clearing CUDA cache before loading avoids this.
    """
    try:
        import torch
        if hasattr(torch, "cuda"):
            torch.cuda.empty_cache()
    except Exception:
        pass

    return LocalEmbedder(
        EmbedderConfig(
            model_name=model_name,
            normalize_embeddings=True,
        )
    )


# ================= FAISS (INCREMENTAL) =================
def build_faiss(chunks: List[Document], embedder: LocalEmbedder) -> None:
    index_path = VECTORSTORE_DIR / "index.faiss"

    if index_path.exists():
        vs = FAISS.load_local(
            str(VECTORSTORE_DIR),
            embedder.langchain_embeddings,
            allow_dangerous_deserialization=True,
        )
        vs.add_documents(chunks)
    else:
        vs = FAISS.from_documents(chunks, embedder.langchain_embeddings)

    vs.save_local(str(VECTORSTORE_DIR))


# ================= API FUNCTION =================
def run_ingestion(file_path: str) -> dict:
    """
    Called by FastAPI /ingest endpoint when user uploads a file.

    Flow:
      1. Clean old bad-path entries from chunks.jsonl  ← fixes old PDFs in answers
      2. Load file
      3. Enrich metadata — source = bare filename only
      4. Chunk with lowered min (30 tokens)
      5. Fallback if still empty
      6. Build/update FAISS
      7. Append to chunks.jsonl for BM25
    """
    # Step 1: Remove old dirty entries every time a new file is ingested
    _clean_chunks_jsonl()

    path = Path(file_path)

    if not path.exists():
        raise ValueError(f"File not found: {file_path}")

    docs = _load_one_file(path)

    if not docs:
        raise ValueError("Unsupported or empty file")

    cfg = IngestConfig(tags=["uploaded", "rag"])
    docs = enrich_metadata(docs, cfg.tags, file_path)
    chunks = chunk_documents(docs, cfg)

    # Fallback: if min-token filter removed everything, keep all non-empty chunks
    if not chunks:
        print("[ingest] WARNING: min-token filter removed all chunks — using fallback")
        length_fn = _token_length_fn_factory(cfg.embedding_model_name)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=cfg.chunk_max_tokens,
            chunk_overlap=cfg.chunk_overlap_tokens,
            length_function=length_fn,
        )
        cleaned = [
            Document(page_content=clean_text(d.page_content), metadata=d.metadata)
            for d in docs
            if clean_text(d.page_content)
        ]
        chunks = [
            c for c in splitter.split_documents(cleaned)
            if c.page_content.strip()
        ]

    if not chunks:
        raise ValueError(
            "No text could be extracted. This PDF may be a scanned image. "
            "Please use a text-based PDF."
        )

    embedder = _make_embedder(cfg.embedding_model_name)
    build_faiss(chunks, embedder)
    save_chunks_jsonl(chunks)

    print(f"[ingest]  Done: {path.name} → {len(chunks)} chunks saved")
    return {"status": "success", "chunks": len(chunks)}


# ================= CLI =================
def main() -> None:
    """
    Bulk ingest all files from src/data/raw/.
    Usage: python -m src.pipelines.ingest
    """
    all_chunks: List[Document] = []
    cfg = IngestConfig(tags=["bulk"])

    for fp in RAW_DIR.rglob("*"):
        if not fp.is_file():
            continue
        loaded = _load_one_file(fp)
        if not loaded:
            print(f"Skipped: {fp}")
            continue
        enriched = enrich_metadata(loaded, cfg.tags, str(fp))
        chunks = chunk_documents(enriched, cfg)
        all_chunks.extend(chunks)
        print(f"  {fp.name} → {len(chunks)} chunks")

    if not all_chunks:
        print("No documents found in src/data/raw/")
        return

    embedder = _make_embedder(cfg.embedding_model_name)
    build_faiss(all_chunks, embedder)
    save_chunks_jsonl(all_chunks)

    print(f"\n Done. Total chunks: {len(all_chunks)}")


if __name__ == "__main__":
    main()