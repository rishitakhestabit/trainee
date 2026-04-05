from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv
from src.utils.schema_loader import DatabaseSchema

load_dotenv()


@dataclass
class SQLGenConfig:
    model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    temperature: float = 0.0
    max_retries: int = 2


_SQL_SYSTEM = """You are a SQL generator.
Rules:
- Output ONLY SQL (no backticks, no explanations).
- Use only the tables/columns provided in the schema.
- Generate a SINGLE SELECT query.
- Do NOT use INSERT/UPDATE/DELETE/DROP/ALTER/PRAGMA/ATTACH.
- Avoid SELECT *; choose relevant columns.
- Use LIMIT 50 unless user explicitly asks for all rows.
"""


def _build_llm(cfg: SQLGenConfig):
    try:
        from langchain_groq import ChatGroq
    except Exception as e:
        raise RuntimeError("Install: pip install -U langchain-groq") from e

    api = os.getenv("GROQ_API_KEY")
    if not api:
        raise RuntimeError("Missing GROQ_API_KEY in .env")

    return ChatGroq(model=cfg.model, temperature=cfg.temperature)


def generate_sql(
    question: str,
    schema: DatabaseSchema,
    cfg: Optional[SQLGenConfig] = None,
    extra_instructions: Optional[str] = None,
) -> str:
    cfg = cfg or SQLGenConfig()
    llm = _build_llm(cfg)

    schema_text = schema.to_prompt_text()
    user_msg = f"""Schema:
{schema_text}

Question:
{question}
"""

    if extra_instructions:
        user_msg += f"\nFix instructions:\n{extra_instructions}\n"

    from langchain_core.messages import SystemMessage, HumanMessage

    resp = llm.invoke([
        SystemMessage(content=_SQL_SYSTEM),
        HumanMessage(content=user_msg)
    ])

    sql = (resp.content or "").strip()
    if sql.startswith("```"):
        sql = sql.replace("```sql", "").replace("```", "").strip()

    return sql


def correct_sql(
    question: str,
    schema: DatabaseSchema,
    bad_sql: str,
    error_msg: str,
    cfg: Optional[SQLGenConfig] = None,
) -> str:
    extra = f"""The previous SQL failed.

Bad SQL:
{bad_sql}

Error:
{error_msg}

Return corrected SQL.
"""
    return generate_sql(question, schema, cfg=cfg, extra_instructions=extra)