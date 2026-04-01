import re, ast
import sqlite3
import pandas as pd
import io as _io
from tools.file_agent import FileAgent
from tools.db_agent import DatabaseAgent
from tools.code_executor import CodeExecutor
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from utils.model_client import get_model_client

def make_agent(name, prompt):
    return AssistantAgent(name=name, model_client=get_model_client(), system_message=prompt)

def clean(text):
    return re.sub(r"```\w*\n?", "", text).strip()

def extract_row_count(query):
    m = re.search(r"\b(\d+)\s*(?:rows?|employees?|entries|items?|students?|products?|records?|orders?)\b", query, re.I)
    return int(m.group(1)) if m else 10

class Orchestrator:
    def __init__(self):
        self.fa        = FileAgent()
        self.db        = DatabaseAgent()
        self.code      = CodeExecutor()
        self.file_meta = {}

        self.planner = make_agent("planner", """
You decide how to handle the user query.
Return ONLY a valid Python list with these keywords:
create_csv, read_csv, analyze, csv_to_db, query_db, modify_db, modify_csv, run_code

RULES — pick the FIRST matching rule:
1. Query mentions "add column", "drop column", "rename column", "fill column", "update column", "update row", "update all", "assign value" with ".db" -> ["modify_db"]
2. Query mentions "add column", "drop column", "rename column", "fill column", "assign value" with ".csv" -> ["modify_csv"]
3. Query mentions "create" + ".csv"           -> ["create_csv"]
4. Query mentions "analyze" or "insights"     -> ["read_csv", "analyze"]
5. Query mentions "convert" + ".csv" + ".db"  -> ["csv_to_db", "query_db"]
6. Query mentions "query" or "select" + ".db" -> ["query_db"]
7. Query is about code/algorithms             -> ["run_code"]
8. Default                                    -> ["run_code"]

Examples:
- "add column bonus to employees.db"                -> ["modify_db"]
- "drop column age from employees.db"               -> ["modify_db"]
- "update row 2 salary to 90000 in employees.db"    -> ["modify_db"]
- "add a column named label to sales.csv"           -> ["modify_csv"]
- "rename column price to cost in sales.csv"        -> ["modify_csv"]
- "create sales.csv with 50 rows"                   -> ["create_csv"]
- "analyze sales.csv"                               -> ["read_csv", "analyze"]
- "convert sales.csv to sales.db"                   -> ["csv_to_db", "query_db"]
- "generate fibonacci"                              -> ["run_code"]
""")

        self.sql_agent = make_agent("sql", """
Convert natural language to a SQLite SELECT query.
Table name: data
All values are TEXT - use CAST(col AS REAL) for numeric comparisons.
Return ONLY the raw SQL SELECT statement. No explanation, no markdown.
Examples:
- top 3 by salary           -> SELECT * FROM data ORDER BY CAST(salary AS REAL) DESC LIMIT 3
- filter HR department      -> SELECT * FROM data WHERE department = 'HR'
- revenue greater than 5000 -> SELECT * FROM data WHERE CAST(revenue AS REAL) > 5000
- cheapest 3 items          -> SELECT * FROM data ORDER BY CAST(price AS REAL) ASC LIMIT 3
- all orders                -> SELECT * FROM data
""")

        self.summarizer = make_agent("summarizer", """
Summarize the result in 2-3 clear helpful lines for the user.
""")

    async def _ask(self, agent, content):
        res = await agent.on_messages([TextMessage(content=content, source="user")], None)
        return res.chat_message.content.strip()

    async def run(self, query):
        t = query.lower()

        # Hard pre-routing — never trust LLM for these unambiguous cases
        if any(k in t for k in ["add column", "drop column", "rename column", "update row", "update all", "fill column"]) and ".db" in t:
            steps = ["modify_db"]
        elif any(k in t for k in ["add column", "drop column", "rename column", "fill column", "assign value"]) and ".csv" in t:
            steps = ["modify_csv"]
        else:
            raw = await self._ask(self.planner, query)
            try:
                steps = ast.literal_eval(clean(raw))
            except Exception:
                steps = re.findall(r"create_csv|read_csv|analyze|csv_to_db|query_db|modify_db|modify_csv|run_code", raw)

        csv_name = FileAgent.detect(query, "csv")
        db_name  = FileAgent.detect(query, "db")
        n_rows   = extract_row_count(query)
        results, data = [], None

        for step in steps:

            if step == "run_code":
                out = await self.code.run(query, show_code=True)
                results.append(f"Output:\n{out}")

            elif step == "create_csv":
                csv_name = csv_name or FileAgent.default_name(query, "csv")
                if csv_name in self.file_meta:
                    n_rows = self.file_meta[csv_name]["rows"]
                raw_out = await self.code.run(
                    f"Generate exactly {n_rows} rows of realistic CSV data for: {query}.\n"
                    f"Use pandas to build a DataFrame with appropriate columns and realistic varied values.\n"
                    f"Print using: print(df.to_csv(index=False))\n"
                    f"Do not save to disk."
                )
                csv_clean = FileAgent.clean_csv(raw_out)
                row_count = len(csv_clean.splitlines()) - 1
                if row_count < 1:
                    results.append("ERROR: Failed to generate CSV content.")
                    break
                self.fa.save(csv_name, csv_clean)
                data = csv_clean
                import csv as _csv
                cols = next(_csv.reader(_io.StringIO(csv_clean)))
                self.file_meta[csv_name] = {"rows": row_count, "columns": cols}
                results.append(f"CSV created: output/{csv_name} ({row_count} rows)\n{csv_clean}")

            elif step == "read_csv":
                csv_name = csv_name or FileAgent.default_name(query, "csv")
                data = self.fa.read(csv_name)
                if data is None:
                    results.append(f"ERROR: {csv_name} not found. Create it first.")
                    break
                results.append(f"Loaded {csv_name} ({len(data.splitlines())-1} rows)\n{data}")

            elif step == "analyze":
                if not data:
                    results.append("ERROR: No data to analyze.")
                    break
                out = await self.code.run(f"Analyze this CSV data and answer: {query}", data)
                results.append(f"Analysis:\n{out}")

            elif step == "csv_to_db":
                if not csv_name:
                    results.append("ERROR: No CSV file to convert.")
                    break
                db_name = self.db.csv_to_db(csv_name)
                results.append(f"Database created: {db_name}")

            elif step == "query_db":
                db_name = db_name or (csv_name.replace(".csv", ".db") if csv_name else None)
                if not db_name:
                    results.append("ERROR: No database found. Mention a .db file or convert a CSV first.")
                    break
                schema = self.db.schema(db_name)
                sql    = clean(await self._ask(self.sql_agent,
                           f"Query: {query}\nColumns available: {schema}"))
                results.append(f"SQL: {sql}\nResults:\n{self.db.query(sql, db_name)}")

            elif step == "modify_db":
                db_name = db_name or (csv_name.replace(".csv", ".db") if csv_name else None)
                if not db_name:
                    results.append("ERROR: No database found.")
                    break
                try:
                    db_path = self.fa.path(db_name)
                    conn    = sqlite3.connect(db_path)
                    df      = pd.read_sql("SELECT * FROM data", conn)
                    conn.close()
                    out = await self.code.run(
                        f"The dataframe is already in variable `df`.\n"
                        f"DO NOT reload or redefine df.\n"
                        f"Use len(df) for any array assignments.\n"
                        f"Task: {query}\n"
                        f"After modification print: print(df.to_csv(index=False))",
                        data=df.to_csv(index=False)
                    )
                    if out.startswith("Execution Error") or out.startswith("ERROR"):
                        results.append(f"ERROR: {out}")
                        break
                    csv_clean = FileAgent.clean_csv(out)
                    lines = [l for l in csv_clean.splitlines() if l.strip()]
                    if len(lines) < 2:
                        results.append("ERROR: No valid data returned.")
                        break
                    df_new = pd.read_csv(_io.StringIO(csv_clean))
                    conn   = sqlite3.connect(db_path)
                    df_new.to_sql("data", conn, if_exists="replace", index=False)
                    conn.close()
                    results.append(f"Database modified: {db_name} ({len(df_new)} rows, columns: {list(df_new.columns)})\n{df_new.to_csv(index=False)}")
                except Exception as e:
                    results.append(f"ERROR: modify_db failed: {e}")

            elif step == "modify_csv":
                csv_name = csv_name or FileAgent.default_name(query, "csv")
                data = self.fa.read(csv_name)
                if data is None:
                    results.append(f"ERROR: {csv_name} not found. Create it first.")
                    break
                out = await self.code.run(
                    f"The CSV data is already in variable `data` as a string.\n"
                    f"Read it with: df = pd.read_csv(io.StringIO(data))\n"
                    f"DO NOT hardcode or re-define the data variable.\n"
                    f"Task: {query}\n"
                    f"Use len(df) to get row count for any array assignments.\n"
                    f"Print the COMPLETE modified CSV using: print(df.to_csv(index=False))",
                    data=data
                )
                if out.startswith("Execution Error") or out.startswith("ERROR"):
                    results.append(f"ERROR: Code agent failed: {out}")
                    break
                csv_clean = FileAgent.clean_csv(out)
                lines = [l for l in csv_clean.splitlines() if l.strip()]
                if len(lines) < 2 or "," not in lines[0]:
                    results.append(f"ERROR: Output is not valid CSV:\n{csv_clean[:200]}")
                    break
                original_rows = self.file_meta.get(csv_name, {}).get("rows", len(lines) - 1)
                if len(lines) - 1 != original_rows:
                    results.append(f"ERROR: Row count mismatch — expected {original_rows}, got {len(lines)-1}. File not saved.")
                    break
                self.fa.save(csv_name, csv_clean)
                import csv as _csv
                cols = next(_csv.reader(_io.StringIO(csv_clean)))
                self.file_meta[csv_name] = {"rows": original_rows, "columns": cols}
                results.append(f"Modified and saved: output/{csv_name} ({original_rows} rows)\n{csv_clean}")
                data = csv_clean

        combined = "\n".join(results)
        summary  = await self._ask(self.summarizer, combined)
        return f"{combined}\n\nSummary:\n{summary}"