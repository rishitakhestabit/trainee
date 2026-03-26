import io
import os
import re
import csv
import json
import sqlite3
import shutil
import pathlib
import re as _re
from typing import Optional
from statistics import mean, stdev
from contextlib import redirect_stdout
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from utils.model_client import get_model_client

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Search order for data files
_SEARCH_DIRS = [
    os.getcwd(),
    BASE_DIR,
    os.path.dirname(BASE_DIR),
    os.path.join(BASE_DIR, "output"),
    os.path.join(os.getcwd(), "output"),
    os.path.join(BASE_DIR, "day3"),
    os.path.join(os.path.dirname(BASE_DIR), "day3"),
]


def _find_file(filename: str) -> Optional[str]:
    if os.path.isabs(filename) and os.path.exists(filename):
        return filename
    for directory in _SEARCH_DIRS:
        candidate = os.path.abspath(os.path.join(directory, filename))
        if os.path.exists(candidate):
            return candidate
    return None


class CodeExecutor:
    def __init__(self):
        self.llm = AssistantAgent(
            name="CodeWriter",
            model_client=get_model_client(),
            system_message=(
            "You are a Python code generator.\n"
            "When given a task, write ONLY executable Python code.\n"
            "Do not include explanations, comments, or markdown.\n"
            "Do not wrap code in backticks.\n"
            "Always use print() to show results.\n"
            "\n"
            "A function called find_file(filename) is already available directly in your code scope.\n"
            "DO NOT import find_file — it is NOT a module, it is a built-in function in scope.\n"
            "WRONG:  import find_file\n"
            "WRONG:  from find_file import find_file\n"
            "CORRECT: path = find_file('sales.csv')\n"
            "\n"
            "Only use find_file when a specific filename is mentioned in the task.\n"
            "If no filename is mentioned, do NOT use find_file at all.\n"
            "If the task says 'sort a list' or 'calculate fibonacci' — just write pure Python, no files.\n"
            "\n"
            "Never construct file paths manually.\n"
            "Never invent filenames that were not mentioned in the task.\n"
            "Use pandas for CSV and tabular data analysis.\n"
            "Write code that adapts to the actual columns in the file.\n"
            "Always handle missing files and missing columns gracefully.\n"
        ),
            )

    # ── Safe execution ────────────────────────────────────────────────────────

    def execute_python(self, code: str) -> str:
        import pandas as pd
        import numpy as np

        out = io.StringIO()
        sandbox = {
            "__builtins__": __builtins__,
            "os": os,
            "pd": pd,
            "np": np,
            "json": json,
            "csv": csv,
            "io": io,
            "find_file": _find_file,
            "shutil": shutil,
            "pathlib": pathlib,
            "re": _re,
        }

        try:
            with redirect_stdout(out):
                exec(code, sandbox, {})
            return out.getvalue().strip() or "Code executed successfully."
        except Exception as e:
            return f"Execution failed: {e}"

    # ── Load CSV ──────────────────────────────────────────────────────────────

    def _load_csv(self, csv_file: str):
        path = _find_file(csv_file)
        if not path:
            raise FileNotFoundError(f"{csv_file} not found")
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames or []
        return rows, fieldnames

    # ── Column type detection ─────────────────────────────────────────────────

    def _detect_numeric_columns(self, rows, fieldnames):
        numeric = []
        for col in fieldnames:
            try:
                [float(r[col]) for r in rows if r[col].strip()]
                numeric.append(col)
            except (ValueError, KeyError):
                pass
        return numeric

    # ── CSV FILTER ────────────────────────────────────────────────────────────

    def _filter_csv(self, task: str, csv_file: str) -> str:
        rows, fieldnames = self._load_csv(csv_file)

        if not rows:
            return "CSV is empty."

        task_lower = task.lower()
        replacements = {
            "greater than": ">",
            "more than":    ">",
            "above":        ">",
            "less than":    "<",
            "below":        "<",
            "equal to":     "=",
        }
        for k, v in replacements.items():
            task_lower = task_lower.replace(k, v)

        match = re.search(r"(\w+)\s+(?:is\s+)?(>=|<=|>|<|=)\s*(\d+)", task_lower)
        if not match:
            return "Could not understand filter condition."

        col, op, value = match.groups()
        value = float(value)

        if col not in fieldnames:
            return f"Column '{col}' not found in CSV."

        filtered = []
        for r in rows:
            try:
                v = float(r[col])
                if (
                    (op == ">"  and v >  value)
                    or (op == "<"  and v <  value)
                    or (op == ">=" and v >= value)
                    or (op == "<=" and v <= value)
                    or (op == "="  and v == value)
                ):
                    filtered.append(r)
            except Exception:
                continue

        if not filtered:
            return "No matching rows found."

        output = ", ".join(fieldnames) + "\n"
        for r in filtered:
            output += ", ".join(r[c] for c in fieldnames) + "\n"
        return output.strip()

    # ── CSV SUMMARY ───────────────────────────────────────────────────────────

    def _summarize_csv(self, csv_file: str) -> str:
        rows, fieldnames = self._load_csv(csv_file)
        if not rows:
            return "The CSV file is empty."

        numeric_cols = self._detect_numeric_columns(rows, fieldnames)
        text_cols    = [c for c in fieldnames if c not in numeric_cols]

        lines = [
            f"The file contains {len(rows)} row(s) and {len(fieldnames)} column(s).",
            f"Columns: {', '.join(fieldnames)}.",
        ]
        for col in numeric_cols:
            values = [float(r[col]) for r in rows if r[col].strip()]
            lines.append(
                f"{col}: total={sum(values):.2f}, min={min(values):.2f}, "
                f"max={max(values):.2f}, mean={mean(values):.2f}."
            )
        for col in text_cols:
            unique_vals = sorted(set(r[col] for r in rows if r[col].strip()))
            lines.append(f"{col}: {len(unique_vals)} unique value(s) — {', '.join(unique_vals)}.")
        return "\n".join(lines)

    # ── CSV INSIGHTS ──────────────────────────────────────────────────────────

    def _insights_csv(self, csv_file: str) -> str:
        rows, fieldnames = self._load_csv(csv_file)
        if not rows:
            return "No insights available — the CSV file is empty."

        numeric_cols = self._detect_numeric_columns(rows, fieldnames)
        text_cols    = [c for c in fieldnames if c not in numeric_cols]
        label_col    = text_cols[0] if text_cols else None

        insights = [f"The dataset has {len(rows)} record(s) across {len(fieldnames)} column(s)."]
        for col in numeric_cols:
            values    = [float(r[col]) for r in rows if r[col].strip()]
            max_row   = max(rows, key=lambda r, c=col: float(r[c]))
            min_row   = min(rows, key=lambda r, c=col: float(r[c]))
            max_label = max_row[label_col] if label_col else "a row"
            min_label = min_row[label_col] if label_col else "a row"
            insights += [
                f"Total {col}: {sum(values):.2f}.",
                f"Average {col}: {mean(values):.2f}.",
                f"Highest {col}: {max_label} ({float(max_row[col]):.2f}).",
                f"Lowest {col}: {min_label} ({float(min_row[col]):.2f}).",
            ]
        for col in text_cols:
            unique_vals = sorted(set(r[col] for r in rows if r[col].strip()))
            insights.append(f"Unique {col} values ({len(unique_vals)}): {', '.join(unique_vals)}.")
        return "\n".join(insights)

    # ── CSV → SQLite ──────────────────────────────────────────────────────────

    def _convert_csv_to_sqlite(self, csv_file: str, db_file: str) -> str:
        path = _find_file(csv_file)
        if not path:
            return f"Conversion failed: '{csv_file}' not found."
        table_name = re.sub(r"[^a-zA-Z0-9_]", "_", os.path.splitext(os.path.basename(csv_file))[0])
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        try:
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.reader(f)
                headers = next(reader)
                columns = ", ".join(f'"{h}" TEXT' for h in headers)
                cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
                cursor.execute(f'CREATE TABLE "{table_name}" ({columns})')
                placeholders = ", ".join(["?"] * len(headers))
                count = 0
                for row in reader:
                    cursor.execute(f'INSERT INTO "{table_name}" VALUES ({placeholders})', row)
                    count += 1
            conn.commit()
            return f"Converted '{csv_file}' → '{db_file}', table '{table_name}', {count} row(s)."
        except Exception as e:
            return f"Conversion failed: {e}"
        finally:
            conn.close()

    # ── CSV GENERATOR — LLM returns raw CSV text, NO code ────────────────────

    async def _llm_generate_csv(self, task: str) -> dict:
        """
        Ask LLM to return ONLY raw CSV text — no Python, no markdown.
        Orchestrator passes this text directly to file_agent to write.
        """
        response = await self.llm.on_messages(
            [TextMessage(
                content=(
                    f"Task: {task}\n\n"
                    "IMPORTANT: Return ONLY raw CSV text.\n"
                    "Do NOT write Python code.\n"
                    "Do NOT use markdown or backticks.\n"
                    "No explanations. No extra text.\n"
                    "Line 1 = header row with exact column names from the task.\n"
                    "Each following line = one data row with realistic values.\n"
                    "Generate exactly the number of rows requested "
                    "(default 10 if not specified).\n"
                    "Use comma as delimiter. No extra spaces.\n"
                    "\n"
                    "Example output format (use actual columns from the task):\n"
                    "product,price,quantity\n"
                    "Laptop,45000,10\n"
                    "Mouse,800,25\n"
                    "Keyboard,1200,15\n"
                ),
                source="user",
            )],
            cancellation_token=None,
        )

        csv_content = response.chat_message.content.strip()

        # Strip any accidental markdown backticks the LLM might add
        csv_content = re.sub(r"^```(?:csv|python)?\s*", "", csv_content, flags=re.MULTILINE)
        csv_content = re.sub(r"```\s*$",                 "", csv_content, flags=re.MULTILINE).strip()

        return {
            "generated_code": "built-in CSV generator",
            "execution_result": csv_content,  # raw CSV text → orchestrator → file agent
        }

    # ── ROUTER ────────────────────────────────────────────────────────────────

    def _resolve_csv(self, task: str) -> Optional[str]:
        match = re.search(r"(\S+\.csv)", task, re.IGNORECASE)
        return match.group(1) if match else None

    def _is_specific_question(self, text: str) -> bool:
        return any(w in text.lower() for w in [
            "greater", "less", "filter", "above", "below",
            "more than", "fewer", "between", "highest", "lowest",
        ])

    async def process_request(self, task: str) -> dict:
        lowered  = task.lower()
        csv_file = self._resolve_csv(task)

        # ── CSV CREATE → LLM generates raw CSV text ───────────────────────────
        # Checked FIRST so it never falls through to analyze/summarize
        if csv_file and any(w in lowered for w in ["create", "generate", "make"]):
            if any(w in lowered for w in ["columns", "rows", "fields", "with", "data", "add"]):
                return await self._llm_generate_csv(task)

        # ── CSV → SQLite ──────────────────────────────────────────────────────
        if csv_file and re.search(r"\S+\.db\b", task, re.IGNORECASE):
            if any(w in lowered for w in ["convert", "create", "make", "save", "load"]):
                db_match = re.search(r"(\S+\.db)\b", task, re.IGNORECASE)
                db_file  = db_match.group(1) if db_match else "output.db"
                return {
                    "generated_code": "built-in CSV→SQLite",
                    "execution_result": self._convert_csv_to_sqlite(csv_file, db_file),
                }

        # ── CSV FILTER ────────────────────────────────────────────────────────
        if csv_file and self._is_specific_question(task):
            return {
                "generated_code": "csv filter",
                "execution_result": self._filter_csv(task, csv_file),
            }

        # ── CSV SUMMARY ───────────────────────────────────────────────────────
        if csv_file and any(w in lowered for w in [
            "read", "show", "display", "open", "view",
            "contents", "summarize", "summary", "explain",
        ]):
            return {
                "generated_code": "built-in CSV summarizer",
                "execution_result": self._summarize_csv(csv_file),
            }

        # ── CSV INSIGHTS ──────────────────────────────────────────────────────
        if csv_file and any(w in lowered for w in [
            "analyze", "analysis", "insight", "insights", "calculate", "total",
        ]):
            return {
                "generated_code": "built-in CSV insights",
                "execution_result": self._insights_csv(csv_file),
            }

        # ── FALLBACK: LLM writes and executes Python code ─────────────────────
        # This handles: pure Python tasks, general questions, code requests
        return await self._llm_analyse(task)

    # ── LLM CODE GENERATOR ───────────────────────────────────────────────────

    async def _llm_analyse(self, task: str) -> dict:
        """Ask the LLM to write and execute Python code for this task."""
        response = await self.llm.on_messages(
            [TextMessage(content=f"Task: {task}", source="user")],
            cancellation_token=None,
        )

        raw = response.chat_message.content.strip()

        # Strip markdown code fences if LLM added them
        match = re.search(r"```python(.*?)```", raw, re.DOTALL)
        if match:
            code = match.group(1).strip()
        else:
            code = re.sub(r"^```.*?\n", "", raw, flags=re.MULTILINE)
            code = re.sub(r"```\s*$",   "", code, flags=re.MULTILINE).strip()

        return {
            "generated_code": code,
            "execution_result": self.execute_python(code),
        }