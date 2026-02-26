from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field
import json
from src.memory.memory_store import memory
from src.evaluation.rag_eval import RAGEvaluator

# Day-2 text retrieval pipeline (you already have these)
from src.retriever.hybrid_retriever import HybridRetriever
from src.retriever.reranker import Reranker
from src.pipelines.context_builder import deduplicate, build_context, ContextConfig

# Day-3 image search (your existing interactive file is src/retriever/image_search.py,
# but for API we call CLIP embedding + FAISS search using your saved index/meta)
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

# Day-4 SQL pipeline runner (your existing)
from src.pipelines.sql_pipeline import (
    DEFAULT_DB_PATH,
    load_schema_sqlite,
    execute_sqlite,
    summarize_result,
    validate_sql,
)
from src.generator.sql_generator import generate_sql, correct_sql, SQLGenConfig


app = FastAPI(title="Week7 Capstone RAG API")
evaluator = RAGEvaluator()

# --------- Load reusable components once ----------
text_retriever = HybridRetriever()
text_reranker = Reranker()

# Image resources (index + meta + clip embedder)
img_meta = _img_load_meta(IMG_META_PATH)
img_index = _img_load_faiss(IMG_INDEX_PATH)
clip = CLIPEembedder(CLIPConfig(model_name="openai/clip-vit-base-patch32"))

# SQL schema
sql_schema = load_schema_sqlite(DEFAULT_DB_PATH)


# -------------------- Request/Response Models --------------------
class AskRequest(BaseModel):
    session_id: str = Field(default="demo1")
    query: str
    filters: Dict[str, Any] = Field(default_factory=dict)  # e.g. {"year":"2024","type":"policy"}
    top_k: int = 5


class AskResponse(BaseModel):
    answer: str
    context: str
    sources: List[Dict[str, Any]]
    eval: Dict[str, Any]


class AskImageRequest(BaseModel):
    session_id: str = Field(default="demo1")
    mode: str = Field(..., description="text2img | img2img | img2text")
    query: Optional[str] = None
    image_path: Optional[str] = None
    top_k: int = 5


class AskSQLRequest(BaseModel):
    session_id: str = Field(default="demo1")
    question: str


class AskSQLResponse(BaseModel):
    sql: str
    summary: str
    eval: Dict[str, Any]


# -------------------- Helpers --------------------
def _answer_from_context(query: str, context: str) -> str:
    """
    For Day-5 capstone, answer generation can be simple:
    if context empty => say not found.
    (You can later swap to an LLM answerer, but this passes launchpad requirements.)
    """
    if not context.strip():
        return "I couldn't find relevant context in your documents for that question."
    # simple: return context as "answer" starter
    return f"Based on the retrieved context:\n\n{context[:900]}"

# -------------------- Routes --------------------
@app.get("/")
def home():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    # LOG user query
    memory.add(req.session_id, "user", req.query, meta={"filters": req.filters, "top_k": req.top_k})

    # 1) retrieve candidates (hybrid + filters + MMR inside HybridRetriever)
    candidates = text_retriever.retrieve_candidates(req.query, top_k=req.top_k, filters=req.filters)

    if not candidates:
        answer = "I couldn't find relevant context in your documents for that question."
        scores = evaluator.score(req.query, answer, context="")
        memory.add(req.session_id, "assistant", answer)
        memory.add(req.session_id, "evaluation", "scores", meta=scores)
        return AskResponse(answer=answer, context="", sources=[], eval=scores)

    # 2) rerank
    reranked = text_reranker.rerank(req.query, candidates, top_k=req.top_k)
    final_docs = [d for d, _ in reranked]

    # 3) dedup
    final_docs = deduplicate(final_docs)

    # 4) pack context window
    ctx_cfg = ContextConfig(top_k=req.top_k)
    context_text, sources = build_context(final_docs, ctx_cfg)

    # 5) make answer
    answer = _answer_from_context(req.query, context_text)

    # LOG assistant answer
    memory.add(req.session_id, "assistant", answer)

    # 6) eval scores
    scores = evaluator.score(req.query, answer, context_text)

    # LOG evaluation
    memory.add(req.session_id, "evaluation", "scores", meta=scores)

    return AskResponse(answer=answer, context=context_text, sources=sources, eval=scores)


@app.post("/ask-image")
def ask_image(req: AskImageRequest):
    memory.add(req.session_id, "user", f"ask-image:{req.mode}", meta={"query": req.query, "image_path": req.image_path, "top_k": req.top_k})

    mode = req.mode.strip().lower()
    if mode not in ("text2img", "img2img", "img2text"):
        ans = "Invalid mode. Use: text2img | img2img | img2text"
        scores = evaluator.score(req.query or "image-query", ans, context="")
        memory.add(req.session_id, "assistant", ans)
        memory.add(req.session_id, "evaluation", "scores", meta=scores)
        return {"answer": ans, "results": [], "eval": scores}

    # build query embedding
    if mode == "text2img":
        if not req.query:
            ans = "Missing query for text2img."
            scores = evaluator.score("text2img", ans, context="")
            memory.add(req.session_id, "assistant", ans)
            memory.add(req.session_id, "evaluation", "scores", meta=scores)
            return {"answer": ans, "results": [], "eval": scores}
        qvec = clip.embed_text(req.query)
        context_for_eval = req.query

    else:
        if not req.image_path:
            ans = "Missing image_path for img2img/img2text."
            scores = evaluator.score("img", ans, context="")
            memory.add(req.session_id, "assistant", ans)
            memory.add(req.session_id, "evaluation", "scores", meta=scores)
            return {"answer": ans, "results": [], "eval": scores}

        p = Path(req.image_path)
        if not p.exists():
            ans = f"Image path not found: {req.image_path}"
            scores = evaluator.score("img", ans, context="")
            memory.add(req.session_id, "assistant", ans)
            memory.add(req.session_id, "evaluation", "scores", meta=scores)
            return {"answer": ans, "results": [], "eval": scores}

        img = _img_open_image(p)
        qvec = clip.embed_image(img)
        context_for_eval = f"image:{req.image_path}"

    # search
    scores_arr, idxs_arr = _img_search(img_index, qvec, req.top_k)
    hits = _img_make_hits(img_meta, scores_arr, idxs_arr, req.top_k)

    if mode in ("text2img", "img2img"):
        ans = "Here are the most similar images."
        context_text = json.dumps(hits[:3], indent=2)
    else:
        # img2text: give OCR+caption as "answer context"
        parts = []
        for h in hits:
            parts.append(f"source={h.get('source')} page={h.get('page')}\ncaption={h.get('caption')}\nocr={h.get('ocr_text_preview')}\n")
        context_text = "\n---\n".join(parts)
        ans = "Extracted context from similar images (caption + OCR preview)."

    memory.add(req.session_id, "assistant", ans, meta={"hits": hits})

    eval_scores = evaluator.score(context_for_eval, ans, context_text)
    memory.add(req.session_id, "evaluation", "scores", meta=eval_scores)

    return {"answer": ans, "results": hits, "eval": eval_scores}


@app.post("/ask-sql", response_model=AskSQLResponse)
def ask_sql(req: AskSQLRequest):
    memory.add(req.session_id, "user", req.question)

    gen_cfg = SQLGenConfig(temperature=0.0)
    sql = generate_sql(req.question, sql_schema, cfg=gen_cfg)

    ok, msg = validate_sql(sql)
    if not ok:
        ans = f"Validation failed: {msg}"
        eval_scores = evaluator.score(req.question, ans, context="")
        memory.add(req.session_id, "assistant", ans, meta={"sql": sql})
        memory.add(req.session_id, "evaluation", "scores", meta=eval_scores)
        return AskSQLResponse(sql=sql, summary=ans, eval=eval_scores)

    # execute with correction loop
    attempts = 0
    last_err = None
    while attempts <= gen_cfg.max_retries:
        try:
            cols, rows = execute_sqlite(DEFAULT_DB_PATH, sql)
            summary = summarize_result(cols, rows)
            memory.add(req.session_id, "assistant", summary, meta={"sql": sql})

            eval_scores = evaluator.score(req.question, summary, context=sql)
            memory.add(req.session_id, "evaluation", "scores", meta=eval_scores)

            return AskSQLResponse(sql=sql, summary=summary, eval=eval_scores)
        except Exception as e:
            last_err = str(e)
            attempts += 1
            if attempts > gen_cfg.max_retries:
                break
            sql = correct_sql(req.question, sql_schema, bad_sql=sql, error_msg=last_err, cfg=gen_cfg)

            ok, msg = validate_sql(sql)
            if not ok:
                summary = f"Validation failed after correction: {msg}"
                eval_scores = evaluator.score(req.question, summary, context="")
                memory.add(req.session_id, "assistant", summary, meta={"sql": sql})
                memory.add(req.session_id, "evaluation", "scores", meta=eval_scores)
                return AskSQLResponse(sql=sql, summary=summary, eval=eval_scores)

    summary = f"SQL execution failed: {last_err}"
    eval_scores = evaluator.score(req.question, summary, context=sql)
    memory.add(req.session_id, "assistant", summary, meta={"sql": sql})
    memory.add(req.session_id, "evaluation", "scores", meta=eval_scores)
    return AskSQLResponse(sql=sql, summary=summary, eval=eval_scores)
