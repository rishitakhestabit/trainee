import re, ast, json
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
        self.fa   = FileAgent()
        self.db   = DatabaseAgent()
        self.code = CodeExecutor()

        self.planner = make_agent("planner", """
You decide how to handle the user query.

If the query is about CSV files, databases, or data (create, read, analyze, convert, query, update):
  Return a Python list using ONLY these keywords:
    create_csv, read_csv, analyze, csv_to_db, query_db, update_db

  Rules:
  - "create and query"      -> ["create_csv", "csv_to_db", "query_db"]
  - "create and analyze"    -> ["create_csv", "analyze"]
  - "convert and query"     -> ["csv_to_db", "query_db"]
  - "read/analyze/insights" -> ["read_csv", "analyze"]
  - Always put csv_to_db before query_db when no .db file is mentioned

If the query is a general coding/programming question (fibonacci, sorting, algorithms, etc.):
  Return exactly: ["run_code"]

Return ONLY a valid Python list. Examples:
- "generate fibonacci"         -> ["run_code"]
- "write a python sort"        -> ["run_code"]
- "create employees.csv"       -> ["create_csv"]
- "analyze sales.csv"          -> ["read_csv", "analyze"]
- "convert sales.csv to db"    -> ["csv_to_db", "query_db"]
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

        self.update_agent = make_agent("updater", """
Extract update details from the request.
Return ONLY valid JSON with exactly these keys: "row" (int), "column" (str), "value" (str).
Example: {"row": 2, "column": "salary", "value": "95000"}
""")

        self.summarizer = make_agent("summarizer", """
Summarize the result in 2-3 clear helpful lines for the user.
""")

    async def _ask(self, agent, content):
        res = await agent.on_messages([TextMessage(content=content, source="user")], None)
        return res.chat_message.content.strip()

    async def run(self, query):
        raw = await self._ask(self.planner, query)
        try:
            steps = ast.literal_eval(clean(raw))
        except Exception:
            steps = re.findall(r"create_csv|read_csv|analyze|csv_to_db|query_db|update_db|run_code", raw)

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
                results.append(f"CSV created: output/{csv_name} ({row_count} rows)")

            elif step == "read_csv":
                csv_name = csv_name or FileAgent.default_name(query, "csv")
                data = self.fa.read(csv_name)
                if data is None:
                    results.append(f"ERROR: {csv_name} not found. Create it first.")
                    break
                results.append(f"Loaded {csv_name} ({len(data.splitlines())-1} rows)")

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
                schema  = self.db.schema(db_name)
                sql     = clean(await self._ask(self.sql_agent,
                            f"Query: {query}\nColumns available: {schema}"))
                results.append(f"SQL: {sql}\nResults:\n{self.db.query(sql, db_name)}")

            elif step == "update_db":
                db_name = db_name or (csv_name.replace(".csv", ".db") if csv_name else None)
                if not db_name:
                    results.append("ERROR: No database found to update.")
                    break
                raw_info = await self._ask(self.update_agent, query)
                try:
                    info = json.loads(clean(raw_info))
                    out  = self.db.update(db_name, info["row"], info["column"], info["value"])
                    results.append(f"Updated row {info['row']}, '{info['column']}' -> '{info['value']}':\n{out}")
                except Exception as e:
                    results.append(f"ERROR: Update failed: {e}")



        combined = "\n".join(results)
        summary  = await self._ask(self.summarizer, combined)
        return f"{combined}\n\nSummary:\n{summary}"