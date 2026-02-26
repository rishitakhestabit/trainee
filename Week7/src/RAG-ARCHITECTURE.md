# Week 7 — Day 1 (LangChain) — Ingestion + Chunking + Embeddings + FAISS + Retriever

## 1-  Day 1 pipeline (full internal flow)

Day 1 has two major stages:

### Stage A — Ingestion & Index Build
File: `src/pipelines/ingest.py`

This stage does:

1. **Load documents**
2. **Clean**
3. **Chunk**
4. **Metadata**
5. **Embeddings**
6. **FAISS store**

#### 1.1 Loading Documents (PDF/TXT/CSV/DOCX)

We load documents from `src/data/raw/` using file extension detection:

- **PDF** → `PyPDFLoader`
  - Produces *page-wise* `Document` objects
  - Usually includes: `metadata["source"]` and `metadata["page"]`
- **TXT / MD** → `TextLoader`
- **CSV** → `CSVLoader` (often 1 doc per row)
- **DOCX / DOC** → `UnstructuredWordDocumentLoader`

Only supported file types are loaded:
`.pdf, .txt, .md, .csv, .docx, .doc`

#### 1.2 Cleaning

We do a minimal but essential cleaning pass:

- Remove null bytes: `\x00`
- Normalize whitespace (convert multiple spaces/newlines to a single space)
- Strip leading/trailing spaces

Why this matters:
- PDFs often contain messy spacing.
- Cleaning improves chunk quality and embedding consistency.

#### 1.3 Chunking (token-aware 500–800)

Taskflow demands **500–800 tokens** chunks.

We use:
- `RecursiveCharacterTextSplitter`
- BUT with a **token length function**, so `chunk_size` is interpreted as tokens (not characters).

How token length is computed:
- If `transformers` tokenizer is available, we load the tokenizer matching the embedding model.
- If not available, we fallback to a rough approximation based on words.

Splitter settings:
- `chunk_size = 800 tokens`
- `chunk_overlap = 80 tokens`
- separators: `["\n\n", "\n", ".", " ", ""]`

Then we filter out very small chunks:
- `chunk_min_tokens = 500`
- This avoids tiny header/table fragments.

Result:
chunks are mostly between 500–800 tokens (with overlap for context continuity).

#### 1.4 Metadata (source, page, tags)

Every chunk/document is guaranteed to have:

- `source` → file path (example: `src/data/raw/astrazeneca_2022.pdf`)
- `page` → page number for PDFs (may be `None` for non-PDF)
- `tags` → list of tags (default: `["week7", "text-rag"]`)

Implementation detail:
We use `metadata.get(...)` safely to avoid crashes when fields are missing.

Why metadata is crucial:
- Retrieval alone is not enough, we need traceability:
  - Where did this chunk come frm-
  - Which page
  - What document

#### 1.5 Embeddings (local)

File: `src/embeddings/embedder.py`

We generate embeddings locally using:
- `HuggingFaceEmbeddings` (LangChain community)

Default model:
- `sentence-transformers/all-MiniLM-L6-v2`

We normalize vectors (recommended for cosine similarity):
- `normalize_embeddings=True`

#### 1.6 FAISS Vector Store

We store vectors in FAISS using:
- `FAISS.from_documents(chunks, embeddings)`

Saved to:
- `src/vectorstore/index.faiss`
- `src/vectorstore/index.pkl`

This is your **searchable local vector database**.

---

### Stage B — Retrieval / Query (run many times)
File: `src/retriever/query_engine.py`

This stage does:

1. Load FAISS index from disk
2. Accept a user query
3. Retrieve top-k relevant chunks
4. Print chunks + metadata (source/page/tags)

#### 1.7 Interactive query loop

We implemented a REPL-style loop:

- The program keeps asking:
  - `Query> ...`
- Runs retrieval
- Prints results
- Stops only when you press Ctrl + C

---

## 2 Commands to Run (simple)

### 2.1 Build FAISS index (first time / whenever docs change)
```bash
python -m src.pipelines.ingest
``

Expected outputs:
- `src/data/chunks/chunks.jsonl`
- `src/vectorstore/index.faiss`
- `src/vectorstore/index.pkl`

### 2.2 Start interactive retriever
```bash
python -m src.retriever.query_engine
```

Example:
```
Query> how is the work culture of astrazeneca
...prints top-k chunks...
Query> (next question)
```

Exit:
- Press `Ctrl+C`

---

