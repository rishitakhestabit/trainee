# (Day 1) — Local RAG System & Pipeline Architecture

## 1) What I built 

My Day-1 RAG system is split into two main stages:

1. **Ingestion **
   - Reads documents from `src/data/raw/`
   - Extracts text + metadata
   - Cleans and chunks the text
   - Generates embeddings for every chunk
   - Stores embeddings in a FAISS vector index
   - Stores chunk metadata in a JSON file parallel to the index

2. **Retrieval **
   - Takes a user query
   - Embeds the query using the same embedding model
   - Searches FAISS for the most similar chunk vectors
   - Returns the best matching chunks along with metadata (source + page)

This is the **Retriever** part of the RAG architecture. 

---

## 2) Folder structure used

The project follows the required Week-7 structure:

```
src/
  data/
    raw/          # input documents (pdf/txt/csv/docx)
    cleaned/      # (optional future) cleaned docs
    chunks/       # generated chunks.json
    embeddings/   # (optional future) saved embeddings
    vectorstore/  # FAISS index + metadata JSON
  embeddings/     # embedder code
  vectorstore/    # FAISS wrapper
  utils/          # loaders + chunking
  pipelines/      # ingestion pipeline
  retriever/      # query engine
  generator/      # LLM client + answer generation
  evaluation/     # sfaithfulness metrics
  prompts/
  models/
  config/
  logs/
```

---

## 3) Components & responsibilities

### A) Document loading — `src/utils/doc_loaders.py`

This module loads different file types and returns a common structure:

- **PDF**: extracted per page (each page becomes a “document unit”)


Each loaded unit looks like:

```json
{
  "text": "...extracted content...",
  "meta": {
    "source": "src/data/raw/<filename>",
    "page": 12,
    "type": "pdf"
  }
}
```

Key metadata fields:
- `source`: file path for traceability  
- `page`: page number for PDFs (None for non-PDF)  
- `type`: pdf/txt/docx/csv  

---

### B) Cleaning + chunking — `src/utils/chunking.py`

This module:
1. **Cleans** text (removes null chars, extra spaces, excessive newlines)
2. **Chunks** the content into **~500–800 token chunks** (approx token count using words)
3. Applies **overlap** between chunks to reduce context loss across boundaries

Each chunk becomes:

```json
{
  "text": "chunk text ...",
  "meta": {
    "source": "...",
    "page": 92,
    "type": "pdf",
    "chunk_id": 1,
    "tags": ["week7", "rag"]
  }
}
```

Notes:
- The chunk size is **token-approx** (word-based), which is acceptable for Day-1.


---

### C) Embeddings — `src/embeddings/embedder.py`

This module generates embeddings locally using SentenceTransformers.

Responsibilities:
- Load embedding model once (e.g., `all-MiniLM-L6-v2`)
- Convert chunk texts → vectors (`float32`)
- Convert user query → vector

Why embeddings?
- They map both query and text chunks into the same vector space
- Similar meaning → vectors closer → retrievable via similarity search

---

### D) Vector storage — `src/vectorstore/faiss_store.py`

This is the FAISS wrapper layer.

What it stores:
- `src/data/vectorstore/index.faiss`  
  → the FAISS index containing all chunk vectors  
- `src/data/vectorstore/index_meta.json`  
  → parallel JSON containing `{text, meta}` for each vector row

Index type:
- Uses a **Flat** index (exact search) for understanding how it works
- Similarity is computed via inner product / cosine (depending on normalization)

Why FAISS?
- Fast vector search
- Simple local persistence
- Industry standard for vector retrieval systems

---

### E) Ingestion pipeline — `src/pipelines/ingest.py`

This is the orchestration file for ingestion.

Flow:
1. Discover files inside `src/data/raw/`
2. Load documents using `doc_loaders.py`
3. Clean + chunk using `chunking.py`
4. Create embeddings using `Embedder`
5. Build FAISS index + save metadata JSON

Outputs generated:
- `src/data/chunks/chunks.json`
- `src/data/vectorstore/index.faiss`
- `src/data/vectorstore/index_meta.json`

---

### F) Retriever / Query Engine — `src/retriever/query_engine.py`

This module provides query-time retrieval.

Flow:
1. Load FAISS index + metadata JSON once at startup
2. Embed user query
3. Search FAISS: top_k most similar chunks
4. Print results with:
   - similarity score
   - `source`, `page`, `chunk_id`
   - chunk preview

It also supports building a **combined context** string (ready for the Generator stage later).

---

## 4) End-to-end workflow

### Step 1 — Put documents
Place files here:

```
src/data/raw/
```

### Step 2 — Ingest documents
Run:

```bash
python -m src.pipelines.ingest
```

This creates:
- `chunks.json`
- `index.faiss`
- `index_meta.json`

### Step 3 — Query / Retrieve
Run:

```bash
python -m src.retriever.query_engine
```

Asking question like:

- `what does the report say about workforce culture?`

will see:
- top retrieved chunks
- scores
- exact traceable `source` + `page`

---

