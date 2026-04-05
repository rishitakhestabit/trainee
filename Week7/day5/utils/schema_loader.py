from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import sqlite3


@dataclass
class TableSchema:
    name: str
    columns: List[Tuple[str, str]]  # (col_name, col_type)


@dataclass
class DatabaseSchema:
    db_path: Path
    tables: List[TableSchema]

    def to_prompt_text(self) -> str:
        lines: List[str] = [f"Database: {self.db_path}"]
        for t in self.tables:
            cols = ", ".join([f"{c} {typ}".strip() for c, typ in t.columns])
            lines.append(f"- {t.name}({cols})")
        return "\n".join(lines)


def load_schema_sqlite(db_path: str | Path) -> DatabaseSchema:
    dbp = Path(db_path)
    if not dbp.exists():
        raise FileNotFoundError(f"SQLite DB not found: {dbp}")

    conn = sqlite3.connect(str(dbp))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        table_names = [r["name"] for r in cur.fetchall()]

        tables: List[TableSchema] = []
        for name in table_names:
            cur.execute(f"PRAGMA table_info('{name}')")
            cols = [(r["name"], r["type"] or "") for r in cur.fetchall()]
            tables.append(TableSchema(name=name, columns=cols))

        return DatabaseSchema(db_path=dbp, tables=tables)
    finally:
        conn.close()