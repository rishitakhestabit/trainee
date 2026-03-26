import re
from typing import List, Dict, Any, Callable, Optional

from tools.code_executor import CodeExecutor
from tools.db_agent import DatabaseAgent
from tools.file_agent import FileAgent


class Orchestrator:
    def __init__(self, database_path: str = "sales.db"):
        self.agents = {
            "code": CodeExecutor(),
            "database": DatabaseAgent(database_path),
            "file": FileAgent(base_dir="."),
        }

    # ── Intent detectors ──────────────────────────────────────────────────────

    def _extract_file_references(self, text: str) -> List[str]:
        return re.findall(r'\b[\w\-.\/\\]+\.(?:csv|txt|db|md)\b', text, flags=re.IGNORECASE)

    def _wants_code(self, text: str) -> bool:
        """User explicitly wants code written or shown."""
        lowered = text.lower()
        return any(phrase in lowered for phrase in [
            "write python", "write code", "show code", "give code",
            "python code", "python function", "write a function",
            "write a script", "code to", "code for",
        ])

    def _is_pure_code_task(self, text: str) -> bool:
        """No file involved — pure computation or code generation."""
        has_file = bool(self._extract_file_references(text))
        return not has_file and (
            self._wants_code(text)
            or any(w in text.lower() for w in [
                "calculate", "compute", "print", "sort", "reverse",
                "fibonacci", "factorial", "prime", "sum of",
            ])
        )

    def _is_list_files_request(self, text: str) -> bool:
        lowered = text.lower().strip()
        return any(p in lowered for p in [
            "list files", "show files", "display files",
            "list all files", "show all files",
        ])

    def _is_read_file_request(self, text: str) -> bool:
        lowered = text.lower()
        files = self._extract_file_references(text)
        return bool(files) and any(w in lowered for w in [
            "read", "show", "display", "open", "view", "contents", "content",
        ])

    def _is_write_file_request(self, text: str) -> bool:
        lowered = text.lower()
        files = self._extract_file_references(text)
        return bool(files) and any(w in lowered for w in [
            "create", "write", "save", "generate", "make",
        ])

    def _is_csv_write_request(self, text: str) -> bool:
        """CSV creation — needs code agent to generate data first."""
        lowered = text.lower()
        return (
            ".csv" in lowered
            and any(w in lowered for w in ["create", "write", "save", "generate", "make"])
            and any(w in lowered for w in ["columns", "rows", "fields", "data", "with"])
        )

    def _is_csv_analysis_request(self, text: str) -> bool:
        lowered = text.lower()
        return ".csv" in lowered and any(w in lowered for w in [
            "summarize", "summary", "analyze", "analysis",
            "insight", "insights", "explain", "calculate", "total",
            "read", "show", "display", "contents",
        ])

    def _is_csv_to_db_request(self, text: str) -> bool:
        lowered = text.lower()
        return ".csv" in lowered and ".db" in lowered and any(
            w in lowered for w in ["convert", "create", "save", "make", "load"]
        )

    def _is_database_request(self, text: str) -> bool:
        lowered = text.lower()
        return ".csv" not in lowered and any(w in lowered for w in [
            ".db", "database", "sqlite", "table", "rows", "records",
            "sql", "query", "select", "top 5", "most expensive", "cheapest",
        ])

    # ── Router ────────────────────────────────────────────────────────────────

    async def analyze_request(self, user_request: str) -> List[str]:
        if self._is_list_files_request(user_request):
            return ["file"]

        if self._is_csv_to_db_request(user_request):
            return ["code"]

        if self._is_csv_analysis_request(user_request):
            return ["file", "code"]

        if self._is_database_request(user_request):
            return ["database"]

        # ── CSV write: code generates data first, then file writes it ─────────
        if self._is_csv_write_request(user_request):
            return ["code", "file"]

        if self._is_write_file_request(user_request) and ".db" not in user_request.lower():
            return ["file"]

        if self._is_read_file_request(user_request):
            return ["file"]

        if self._is_pure_code_task(user_request):
            return ["code"]

        # Default
        return ["code"]

    # ── Execution ─────────────────────────────────────────────────────────────

    async def execute_with_agents(
        self,
        user_request: str,
        agent_names: List[str],
        status_callback: Optional[Callable[[str], None]] = None,
    ) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        for name in agent_names:
            if status_callback:
                status_callback(f"Running {name} agent...")

            # ── File agent after code agent ───────────────────────────────────
            if name == "file" and "code" in results:

                code_result = results["code"]

                # Extract the generated CSV content from code agent output
                # if isinstance(code_result, dict):
                #     csv_content = (
                #         code_result.get("execution_result", "")
                #         or code_result.get("generated_code", "")
                #     ).strip()
                # else:
                #     csv_content = str(code_result).strip()

                if isinstance(code_result, dict):
                    csv_content = code_result.get("execution_result", "").strip()

                    # fallback if empty
                    if not csv_content:
                        csv_content = code_result.get("generated_code", "").strip()
                else:
                    csv_content = str(code_result).strip()

                # prevent empty file creation
                if not csv_content:
                    results[name] = "Error: No CSV content generated by code agent."
                    continue

                # If code agent produced CSV-like content, pass it to file agent
                if csv_content and "," in csv_content:
                    enriched = (
                        f"{user_request}\n\n"
                        f"--- Generated CSV content (write this exactly) ---\n"
                        f"{csv_content}"
                    )
                else:
                    # Code agent didn't produce CSV data — let file agent handle it alone
                    enriched = user_request

                results[name] = await self.agents[name].process_request(enriched)

            # ── Code agent after file agent (analysis) ────────────────────────
            elif name == "code" and "file" in results:
                enriched = (
                    f"{user_request}\n\n"
                    f"--- Data from file ---\n{results['file']}"
                )
                results[name] = await self.agents[name].process_request(enriched)

            # ── All other agents run independently ────────────────────────────
            else:
                results[name] = await self.agents[name].process_request(user_request)

        return results

    # ── Synthesis ─────────────────────────────────────────────────────────────

    async def synthesize_results(
        self,
        user_request: str,
        results: Dict[str, Any],
    ) -> str:
        wants_code = self._wants_code(user_request)

        if "database" in results:
            return str(results["database"]).strip()

        if "file" in results and "code" in results:
            # CSV write: show file agent result (confirmation of what was written)
            if self._is_csv_write_request(user_request):
                return str(results["file"]).strip()
            # CSV analysis: show code agent result
            code_result = results["code"]
            if isinstance(code_result, dict):
                if wants_code:
                    return code_result.get("generated_code", "").strip()
                return code_result.get("execution_result", "").strip()
            return str(code_result).strip()

        if "file" in results:
            return str(results["file"]).strip()

        if "code" in results:
            code_result = results["code"]
            if isinstance(code_result, dict):
                if wants_code:
                    generated = code_result.get("generated_code", "").strip()
                    executed  = code_result.get("execution_result", "").strip()
                    parts = []
                    if generated:
                        parts.append(f"Generated code:\n{generated}")
                    if executed and executed != generated:
                        parts.append(f"Output:\n{executed}")
                    return "\n\n".join(parts) if parts else "No output."
                return code_result.get("execution_result", "").strip()
            return str(code_result).strip()

        return "Task completed successfully."

    # ── Entry point ───────────────────────────────────────────────────────────

    async def process_request(
        self,
        user_request: str,
        status_callback: Optional[Callable[[str], None]] = None,
    ) -> Dict[str, Any]:
        if status_callback:
            status_callback("Analyzing request...")

        agent_names = await self.analyze_request(user_request)

        if status_callback:
            status_callback(f"Using agents: {', '.join(agent_names)}")

        results = await self.execute_with_agents(
            user_request=user_request,
            agent_names=agent_names,
            status_callback=status_callback,
        )

        if status_callback:
            status_callback("Synthesizing results...")

        final_answer = await self.synthesize_results(user_request, results)

        return {
            "final_answer": final_answer,
            "agents_used": agent_names,
            "agent_results": results,
        }