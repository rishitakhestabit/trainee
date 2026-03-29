import time
from dotenv import load_dotenv
load_dotenv()
import json
from pathlib import Path
from typing import Any, Dict, Optional
import requests as http_requests  
import os                          
from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.memory.memory_store import memory
from src.evaluation.rag_eval import RAGEvaluator

# Text RAG
from src.retriever.hybrid_retriever import HybridRetriever
from src.retriever.reranker import Reranker
from src.pipelines.context_builder import deduplicate, build_context, ContextConfig
from src.pipelines.ingest import run_ingestion

# Image RAG
from src.retriever.image_search import (
    META_PATH as IMG_META_PATH,
    INDEX_PATH as IMG_INDEX_PATH,
    _load_meta as _img_load_meta,
    _load_faiss as _img_load_faiss,
    _make_hits as _img_make_hits,
    _search as _img_search,
    _safe_open_image as _img_open_image,
)
from src.embeddings.clip_embedder import CLIPConfig, CLIPEembedder

# SQL
from src.pipelines.sql_pipeline import (
    DEFAULT_DB_PATH,
    load_schema_sqlite,
    execute_sqlite,
    summarize_result,
    validate_sql,
)
from src.generator.sql_generator import generate_sql, correct_sql, SQLGenConfig


app = FastAPI(title="Production RAG System")
evaluator = RAGEvaluator()

# ================= INIT =================
# HybridRetriever loads chunks.jsonl ONCE at startup to build BM25.
# After a new PDF is ingested, we must reload it so BM25 sees new chunks.
# We store it in a mutable dict so the /ingest endpoint can replace it.
_state: Dict[str, Any] = {}

def _init_retriever():
    """Load (or reload) the HybridRetriever and store in _state."""
    _state["retriever"] = HybridRetriever()

def get_retriever() -> HybridRetriever:
    if "retriever" not in _state:
        _init_retriever()
    return _state["retriever"]

# Initial load at startup
_init_retriever()

reranker = Reranker()

img_meta = _img_load_meta(IMG_META_PATH)
img_index = _img_load_faiss(IMG_INDEX_PATH)
clip = CLIPEembedder(CLIPConfig())

sql_schema = load_schema_sqlite(DEFAULT_DB_PATH)


# ================= MODELS =================
class AskRequest(BaseModel):
    session_id: str = "demo"
    query: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    top_k: int = 5


class AskImageRequest(BaseModel):
    session_id: str = "demo"
    mode: str
    query: Optional[str] = None
    image_path: Optional[str] = None
    top_k: int = 3


class AskSQLRequest(BaseModel):
    session_id: str = "demo"
    question: str


# ================= HELPER =================
def _answer_from_context(query: str, context: str) -> str:
    if not context.strip():
        return "No relevant information found."
    return f"Based on context:\n\n{context[:900]}"


# ADD THIS FUNCTION BELOW IT
def generate_answer(query: str, context: str) -> str:
    if not context.strip():
        return "No relevant information found."
    
    prompt = f"""You are a helpful assistant. Answer the question using ONLY the context below.
"

Context:
{context}

Question: {query}

Answer:"""

    try:
        res = http_requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0
            }
        )
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Generation failed: {str(e)}"
# ================= SOURCE FILTER =================
def extract_source_from_query(query: str, candidates) -> Optional[str]:
    """
    Check if user mentioned a PDF filename in their query.
    e.g. "what is RAG in week-7" → matches "Week-7-1766484412108.pdf"
    Uses fuzzy prefix matching so user doesn't need the full filename.
    """
    query_lower = query.lower()

    for d in candidates:
        source = str(d.metadata.get("source", "")).lower()
        clean_source = source.replace(".pdf", "")  # strip extension for matching

        if clean_source and clean_source in query_lower:
            return d.metadata.get("source")

    return None


# =========================================================
# TEXT RAG
# =========================================================
@app.post("/ask")
def ask(req: AskRequest):
    start = time.time()

    try:
        memory.add(req.session_id, "user", req.query)

        # Always use the current retriever (reloaded after each ingest)
        retriever = get_retriever()

        # -------- RETRIEVE --------
        candidates = retriever.retrieve_candidates(
            req.query, top_k=req.top_k, filters=req.filters
        )

        # Check if user mentioned a specific PDF by name
        source_filter = extract_source_from_query(req.query, candidates)

        if source_filter:
            # User named a file → filter to only that file's chunks
            candidates = [
                d for d in candidates
                if d.metadata.get("source") == source_filter
            ]
        # else: no filter → retriever already sorted by latest uploaded_at

        if not candidates:
            answer = "No context found."
            scores = evaluator.score(req.query, answer, "")
            return {
                "answer": answer,
                "eval": {**scores, "latency": round(time.time() - start, 3)}
            }

        # -------- RERANK --------
        reranked = reranker.rerank(req.query, candidates, top_k=req.top_k)

        docs = []
        for item in reranked:
            if isinstance(item, tuple):
                docs.append(item[0])
            else:
                docs.append(item)

        docs = deduplicate(docs)

        # -------- CONTEXT --------
        result = build_context(docs, ContextConfig(top_k=req.top_k))

        if isinstance(result, tuple) and len(result) == 2:
            context, sources = result
        else:
            context = result if isinstance(result, str) else ""
            sources = []

        answer = generate_answer(req.query, context)

        # -------- EVALUATION --------
        scores = evaluator.score(req.query, answer, context)

        # -------- SELF REFLECTION --------

        if scores.get("confidence", 1.0) < 0.4 or scores.get("hallucination", 0) == 1:
            answer = "Low confidence or hallucinated answer. Please verify."
            scores = evaluator.score(req.query, answer, context)

        memory.add(req.session_id, "assistant", answer)
        memory.add(req.session_id, "evaluation", "scores", meta=scores)

        return {
            "answer": answer,
            "sources": sources,
            "eval": {**scores, "latency": round(time.time() - start, 3)}
        }

    except Exception as e:
        return {"error": str(e)}


# =========================================================
# IMAGE RAG
# =========================================================
@app.post("/ask-image")
def ask_image(req: AskImageRequest):
    start = time.time()

    try:
        if req.mode == "text2img":
            if not req.query:
                return {"error": "Query required for text2img"}
            vec = clip.embed_text(req.query)

        elif req.mode == "img2img":
            if not req.image_path:
                return {"error": "Image required for img2img"}
            img_path = Path(req.image_path)
            if not img_path.exists():
                return {"error": "Image path not found"}
            img = _img_open_image(img_path)
            vec = clip.embed_image(img)

        else:
            return {"error": "Invalid mode"}

        scores_arr, idxs_arr = _img_search(img_index, vec, req.top_k)
        hits = _img_make_hits(img_meta, scores_arr, idxs_arr, req.top_k)

        # Generate short description for each image
        for hit in hits:
            caption = hit.get("caption", "")
            ocr = hit.get("ocr_text_preview", "")
            context_text = f"Caption: {caption}\nOCR Text: {ocr}".strip()

            if context_text:
                try:
                    res = http_requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                            "messages": [{"role": "user", "content": f"Give a single short 1-2 sentence description of this image based on the following info:\n{context_text}"}],
                            "temperature": 0.0,
                            "max_tokens": 100
                        }
                    )
                    hit["description"] = res.json()["choices"][0]["message"]["content"].strip()
                except Exception:
                    hit["description"] = caption or "No description available."
            else:
                hit["description"] = "No description available."

        return {
            "results": hits[:3],
            "eval": {"latency": round(time.time() - start, 3)}
        }

    except Exception as e:
        return {"error": str(e)}


# =========================================================
# SQL RAG
# =========================================================
@app.post("/ask-sql")
def ask_sql(req: AskSQLRequest):
    start = time.time()

    try:
        memory.add(req.session_id, "user", req.question)

        cfg = SQLGenConfig(temperature=0.0)
        sql = generate_sql(req.question, sql_schema, cfg=cfg)

        ok, msg = validate_sql(sql)
        if not ok:
            return {"error": msg}

        attempts = 0
        while attempts <= cfg.max_retries:
            try:
                cols, rows = execute_sqlite(DEFAULT_DB_PATH, sql)
                summary = summarize_result(cols, rows)
                eval_scores = evaluator.score(req.question, summary, sql)
                return {
                    "sql": sql,
                    "summary": summary,
                    "eval": {**eval_scores, "latency": round(time.time() - start, 3)}
                }
            except Exception as e:
                attempts += 1
                sql = correct_sql(req.question, sql_schema, sql, str(e), cfg)

        return {"error": "SQL failed after retries"}

    except Exception as e:
        return {"error": str(e)}


# =========================================================
# INGEST
# =========================================================
@app.post("/ingest")
def ingest(data: dict):
    try:
        if "file_path" not in data:
            return {"error": "file_path missing"}

        # Run ingestion — saves to FAISS + chunks.jsonl
        result = run_ingestion(data["file_path"])

        _init_retriever()
        print("[app] HybridRetriever reloaded with latest chunks.jsonl")

        return result

    except Exception as e:
        return {"error": str(e)}