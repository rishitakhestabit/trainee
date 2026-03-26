import re
import sqlite3
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from utils.model_client import get_model_client


class DatabaseAgent:
    def __init__(self, db_path: str = "sales.db"):
        self.db_path = db_path
        self.agent = AssistantAgent(
            name="DatabaseAgent",
            model_client=get_model_client(),
            system_message=(
                "You are a SQLite query generator.\n"
                "Generate exactly one valid SQLite query.\n"
                "\n"
                "RULES:\n"
                "1. Return only raw SQL.\n"
                "2. Do not include explanations.\n"
                "3. Do not use markdown.\n"
                "4. Do not wrap SQL in backticks.\n"
                "5. Generate only one SQL statement.\n"
                "6. Use SELECT for read-only requests.\n"
                "7. Use INSERT, UPDATE, or DELETE only if the user explicitly asks to modify data.\n"
                "8. Never generate CREATE TABLE, DROP TABLE, or ALTER TABLE.\n"
                "9. Use only SQLite-compatible syntax.\n"
                "10. Prefer the provided table name if available.\n"
            ),
        )

    def _get_table_names(self) -> list[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

    def _choose_table_name(self, task: str) -> str | None:
        tables = self._get_table_names()
        if not tables:
            return None

        lowered = task.lower()

        for table in tables:
            if table.lower() in lowered:
                return table

        if "sales.db" in lowered and "sales" in tables:
            return "sales"

        return tables[0]

    def _build_direct_query(self, task: str, table_name: str) -> str | None:
        lowered = task.lower()

        if "all rows" in lowered or "display all rows" in lowered or "show all rows" in lowered:
            return f'SELECT * FROM "{table_name}";'

        if "top 5" in lowered and ("expensive" in lowered or "highest price" in lowered or "costliest" in lowered):
            return f'SELECT * FROM "{table_name}" ORDER BY CAST(price AS REAL) DESC LIMIT 5;'

        if "top 5" in lowered and ("cheapest" in lowered or "lowest price" in lowered):
            return f'SELECT * FROM "{table_name}" ORDER BY CAST(price AS REAL) ASC LIMIT 5;'

        if "count" in lowered and "rows" in lowered:
            return f'SELECT COUNT(*) AS total_rows FROM "{table_name}";'

        if "product and price" in lowered:
            return f'SELECT product, price FROM "{table_name}";'

        if "sales greater than" in lowered:
            match = re.search(r"sales greater than (\d+)", lowered)
            if match:
                value = match.group(1)
                return f'SELECT * FROM "{table_name}" WHERE CAST(sales AS REAL) > {value};'

        return None

    def _execute_sql(self, query: str) -> str:
        lowered = query.strip().lower()

        blocked_keywords = ["create table", "drop table", "alter table"]
        if any(keyword in lowered for keyword in blocked_keywords):
            return "Blocked unsafe SQL operation (DDL is not allowed)."

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(query)

            if lowered.startswith("select"):
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                if not rows:
                    return "Query executed successfully but returned no rows."

                output = " | ".join(columns) + "\n"
                output += "-" * 50 + "\n"
                for row in rows[:100]:
                    output += " | ".join(str(value) for value in row) + "\n"

                return output.strip()

            conn.commit()
            return f"Query executed successfully. Rows affected: {cursor.rowcount}"

        except sqlite3.Error as e:
            return f"SQL Error: {e}"

        finally:
            conn.close()

    async def process_request(self, task: str):
        table_name = self._choose_table_name(task)

        if not table_name:
            return "SQL Error: No tables found in the database."

        direct_query = self._build_direct_query(task, table_name)

        if direct_query:
            sql_query = direct_query
        else:
            prompt = (
                f"User request: {task}\n"
                f"Use this table name: {table_name}\n"
                "Return only one valid SQLite query."
            )

            response = await self.agent.on_messages(
                [TextMessage(content=prompt, source="user")],
                cancellation_token=None,
            )
            sql_query = response.chat_message.content.strip()

        print("\n--- GENERATED SQL ---\n", sql_query)
        return self._execute_sql(sql_query)