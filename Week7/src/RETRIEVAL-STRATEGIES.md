# DAY 2 — Advanced Retrieval + Context Engineering (Week7)

This day was about making retrieval, so the LLM gets **better context** (less random chunks) and the answer becomes **more accurate + less hallucination**.

---

## What I built (step by step)

### 1) Hybrid Retrieval (Semantic + Keyword)
Goal: if embeddings miss something, **BM25 keyword search** can still catch it.

- **Semantic search (FAISS + embeddings)** - understands meaning.
- **Keyword search (BM25)** → catches exact words / names / terms.
- Then I **merge both scores** into one final score.

File: `src/retriever/hybrid_retriever.py`

---

### 2) Filters support (year/type)
Goal: allow queries like:

```python
query = "Explain how credit underwriting works"
top_k = 5
filters = {"year": "2024", "type": "policy"}
```

If metadata is missing, I still try to pass filters using a fallback:
- **year** inferred from filename/path if it contains `YYYY`
- **type** inferred from `tags` or source path

 File: `src/retriever/hybrid_retriever.py` (`_passes_filters()`)

---

### 3) MMR (Max Marginal Relevance) for diversity
Problem: top results can be repetitive (same topic, same chunk style).

Solution: after getting a candidate pool, I use **MMR** to pick chunks that are:
- relevant to query
- but not duplicates of each other

File: `src/retriever/hybrid_retriever.py` (`_mmr_select()`)

---

### 4) Reranking (Cross Encoder / fallback cosine)
Hybrid retrieval gives a good candidate list, but final ordering is improved using **reranking**:

- Best case: **CrossEncoder reranker** (more accurate scoring)
- Fallback: cosine similarity rerank using embeddings

File: `src/retriever/reranker.py`

---

### 5) Deduplication
Even after MMR/reranking, duplicates can still appear (same chunk stored multiple times).

So I remove duplicates using a hash of chunk text.

File: `src/pipelines/context_builder.py` (`deduplicate()`)

---

### 6) Context packing (context window optimization)
LLM context is limited, so I don’t blindly dump everything.

I pack context until a **token budget** is hit:
- keep short headers (source/page/year/type/tags)
- keep a body preview (to reduce terminal spam)
- stop when token budget reached

File: `src/pipelines/context_builder.py` (`build_context()`)

---

### 7) Traceable sources 
Along with the final context, I also output a structured `sources[]` list so we can always see:

- which file
- which page
- rank
- preview

File: `src/pipelines/context_builder.py` (`sources` list)

---

## What each file does

### `src/retriever/hybrid_retriever.py`
Responsible for:
- Loading FAISS vectorstore (`src/vectorstore/`)
- Loading chunk corpus from `src/data/chunks/chunks.jsonl`
- Building BM25 index
- Running hybrid search:
  - vector candidates + BM25 candidates
  - normalize scores
  - merge with `alpha`
  - apply filters
  - apply MMR (optional)
- Returns **candidate documents** to reranker

---

### `src/retriever/reranker.py`
Responsible for:
- Reranking candidate docs using:
  - `CrossEncoder` if available
  - otherwise cosine similarity fallback
- Returns **top_k docs with scores**

---

### `src/pipelines/context_builder.py`
Responsible for:
- Running the full Day-2 pipeline in order:
  1. hybrid retrieval
  2. rerank
  3. deduplicate
  4. pack context (token budget)
  5. print final context + sources
- Also provides an **interactive CLI mode**:
  - if you run it without `--query`

## Screenshots (Day-2 results)

### Run output (example 1)
![Day-2 output 1](src/ss/day2ss/queryres.png)

### Run output (example 2)
![Day-2 output 2](src/ss/day2ss/queryres2.png)

