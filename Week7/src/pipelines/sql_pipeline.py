from __future__ import annotations

import argparse
import csv
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.utils.schema_loader import load_schema_sqlite, DatabaseSchema
from src.generator.sql_generator import generate_sql, correct_sql, SQLGenConfig


# -------------------------
# Defaults for your dataset
# -------------------------
DEFAULT_CSV_PATH = Path("src/data/sql/customers1000.csv")
DEFAULT_DB_PATH = Path("src/data/sql/customers.db")
DEFAULT_TABLE_NAME = "customers"


# -------------------------
# SQL safety / validation
# -------------------------
_DISALLOWED = [
    r"\binsert\b",
    r"\bupdate\b",
    r"\bdelete\b",
    r"\bdrop\b",
    r"\balter\b",
    r"\battach\b",
    r"\bdetach\b",
    r"\bpragma\b",
    r"\bvacuum\b",
    r"\bcreate\b",
    r"\breplace\b",
    r"\btruncate\b",
    r";",  # no multi-statement
]
_ALLOWED_START = re.compile(r"^\s*select\b", re.IGNORECASE)


def validate_sql(sql: str) -> Tuple[bool, str]:
    s = (sql or "").strip()
    if not s:
        return False, "Empty SQL."
    if not _ALLOWED_START.search(s):
        return False, "Only SELECT queries are allowed."

    lower = s.lower()
    for pat in _DISALLOWED:
        if re.search(pat, lower):
            return False, f"Disallowed token/pattern detected: {pat}"

    return True, "OK"


# -------------------------
# CSV -> SQLite builder
# -------------------------
_SQL_RESERVED = {
    # common SQLite/SQL keywords that appear as CSV headers
    "index",
    "table",
    "select",
    "from",
    "where",
    "group",
    "order",
    "by",
    "limit",
}


def _normalize_col(col: str) -> str:
    """Turn 'Subscription Date' -> 'subscription_date'"""
    col = col.strip().lower()
    col = re.sub(r"[^a-z0-9]+", "_", col)
    col = re.sub(r"_+", "_", col).strip("_")
    if not col:
        col = "col"
    return col


def _safe_col_name(col: str) -> str:
    """Handle reserved keywords + ensure stable naming."""
    if col in _SQL_RESERVED:
        if col == "index":
            return "row_index"
        return f"{col}_col"
    return col


def _q_ident(name: str) -> str:
    """Quote an identifier for SQLite using double quotes."""
    return '"' + name.replace('"', '""') + '"'


def build_sqlite_from_csv(
    csv_path: Path,
    db_path: Path,
    table_name: str = DEFAULT_TABLE_NAME,
) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    db_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row.")

        raw_cols = reader.fieldnames
        norm_cols = [_safe_col_name(_normalize_col(c)) for c in raw_cols]

        rows: List[List[str]] = []
        for r in reader:
            rows.append([r.get(c, "") for c in raw_cols])

    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()

        # Drop & recreate table
        cur.execute(f'DROP TABLE IF EXISTS {_q_ident(table_name)}')

        # All TEXT columns for simplicity
        col_defs = ", ".join([f"{_q_ident(c)} TEXT" for c in norm_cols])
        cur.execute(f'CREATE TABLE {_q_ident(table_name)} ({col_defs})')

        placeholders = ", ".join(["?"] * len(norm_cols))
        insert_sql = f'INSERT INTO {_q_ident(table_name)} VALUES ({placeholders})'
        cur.executemany(insert_sql, rows)

        conn.commit()
    finally:
        conn.close()

    print(f"[CSV→SQLITE] Built DB: {db_path}")
    print(f"[CSV→SQLITE] Table: {table_name}")
    print("[CSV→SQLITE] Column mapping (original -> db):")
    for a, b in zip(raw_cols, norm_cols):
        print(f"  - {a} -> {b}")


# -------------------------
# Safe executor (SQLite)
# -------------------------
def execute_sqlite(db_path: Path, sql: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        data = [dict(r) for r in rows]
        return cols, data
    finally:
        conn.close()


# -------------------------
# Result summarizer
# -------------------------
def summarize_result(columns: List[str], rows: List[Dict[str, Any]], max_rows_preview: int = 10) -> str:
    if not columns:
        return "Query executed, but returned no columns."
    n = len(rows)
    if n == 0:
        return "No rows returned."

    preview = rows[:max_rows_preview]
    lines: List[str] = []
    lines.append(f"Returned {n} row(s). Showing first {min(n, max_rows_preview)}:")
    lines.append("Columns: " + ", ".join(columns))

    for i, r in enumerate(preview, start=1):
        compact = ", ".join([f"{k}={r.get(k)}" for k in columns[:8]])
        lines.append(f"{i}. {compact}")

    return "\n".join(lines)


# -------------------------
# Pipeline
# -------------------------
@dataclass
class PipelineConfig:
    db_path: Path
    # Model can be set via CLI; if None, SQLGenConfig will fall back to GROQ_MODEL from .env
    llm_model: Optional[str] = None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Day-4 SQL QA: Text -> SQL -> Answer (CSV→SQLite supported)")
    p.add_argument("--csv_path", type=str, default=str(DEFAULT_CSV_PATH))
    p.add_argument("--db_path", type=str, default=str(DEFAULT_DB_PATH))
    p.add_argument(
        "--model",
        type=str,
        default=None,
        help="Groq model name. If omitted, uses GROQ_MODEL from .env (recommended).",
    )
    p.add_argument("--rebuild_db", action="store_true", help="Force rebuild SQLite from CSV")
    return p.parse_args()


def run_once(question: str, schema: DatabaseSchema, cfg: PipelineConfig) -> None:
    # If cfg.llm_model is not provided, SQLGenConfig will use GROQ_MODEL from .env
    if cfg.llm_model:
        gen_cfg = SQLGenConfig(model=cfg.llm_model, temperature=0.0)
    else:
        gen_cfg = SQLGenConfig(temperature=0.0)

    sql = generate_sql(question, schema, cfg=gen_cfg)

    ok, msg = validate_sql(sql)
    if not ok:
        print("\n[VALIDATION FAILED]")
        print(msg)
        print("LLM produced:\n", sql)
        return

    attempts = 0
    last_err: Optional[str] = None
    while attempts <= gen_cfg.max_retries:
        try:
            cols, rows = execute_sqlite(schema.db_path, sql)
            print("\n===== GENERATED SQL =====\n")
            print(sql)
            print("\n===== SUMMARY =====\n")
            print(summarize_result(cols, rows))
            return
        except Exception as e:
            last_err = str(e)
            attempts += 1
            if attempts > gen_cfg.max_retries:
                break

            sql = correct_sql(question, schema, bad_sql=sql, error_msg=last_err, cfg=gen_cfg)
            ok, msg = validate_sql(sql)
            if not ok:
                print("\n[VALIDATION FAILED AFTER CORRECTION]")
                print(msg)
                print("LLM produced:\n", sql)
                return

    print("\n[EXECUTION FAILED]")
    print("Error:", last_err)
    print("Last SQL:\n", sql)


def main():
    args = parse_args()
    csv_path = Path(args.csv_path)
    db_path = Path(args.db_path)

    if args.rebuild_db or (not db_path.exists()):
        build_sqlite_from_csv(csv_path, db_path, table_name=DEFAULT_TABLE_NAME)

    schema = load_schema_sqlite(db_path)
    cfg = PipelineConfig(db_path=db_path, llm_model=args.model)

    print("\n=== Day-4 SQL-QA Engine ===")
    print("DB:", db_path)
    print("\nLoaded schema:\n")
    print(schema.to_prompt_text())
    print("\nType a question and press Enter. Ctrl+C to exit.\n")

    try:
        while True:
            q = input("Question> ").strip()
            if not q:
                continue
            run_once(q, schema, cfg)
    except KeyboardInterrupt:
        print("\nExiting.\n")


if __name__ == "__main__":
    main()