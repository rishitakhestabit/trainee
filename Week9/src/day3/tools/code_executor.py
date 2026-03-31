import re, io, csv, json, contextlib
import pandas as pd
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from utils.model_client import get_model_client

class CodeExecutor:
    def __init__(self):
        self.agent = AssistantAgent(
            name="coder",
            model_client=get_model_client(),
            system_message="""You generate clean executable Python code only.
Rules:
- pandas is available as `pd`, io is available as `io`
- CSV data is in variable `data` (string) - read with: df = pd.read_csv(io.StringIO(data))
- Always print() every result
- Return ONLY raw Python code, no markdown, no backticks, no explanation"""
        )

    async def run(self, task, data=None, show_code=False):
        prompt = f"{task}\n\nThe CSV data is in variable `data` as a string." if data else task
        res = await self.agent.on_messages([TextMessage(content=prompt, source="user")], None)
        code = re.sub(r"```\w*\n?", "", res.chat_message.content).strip()
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                exec(compile(code, "<string>", "exec"), {
                    "pd": pd, "io": io, "csv": csv, "json": json, "data": data
                })
            output = buf.getvalue().strip() or "Done"
            if show_code:
                return f"Code:\n{code}\n\nOutput:\n{output}"
            return output
        except Exception as e:
            return f"Execution Error: {e}\nCode:\n{code}"