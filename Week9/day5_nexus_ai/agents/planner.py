from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from loader import LLMClient
from pydantic import BaseModel, Field
from typing import Literal, List
import asyncio


AgentName = Literal[
    "Researcher",
    "Coder",
    "Analyst",
    "Critic",
    "Optimizer",
    "Validator",
    "Reporter"
]


class PlanStep(BaseModel):
    agent: AgentName
    instruction: str
    depends_on: List[AgentName] = Field(default_factory=list)


class ExecutionPlan(BaseModel):
    steps: List[PlanStep]


PLANNER_PROMPT = """
You are an expert Planner Agent for a multi-agent AI system.

Your role is to generate a clean, correct execution plan.

You must:
1. Break the user request into clear steps
2. Assign each step to the correct agent
3. Define dependencies correctly (no cycles)
4. Return ONLY valid JSON (ExecutionPlan schema)

----------------------------------------
AVAILABLE AGENTS

Researcher:
- Research topics, trends, architecture, strategies
- Used for: planning, ideas, system design, RAG research

Analyst:
- ONLY for data/CSV/database analysis
- Used when task mentions: CSV, data, metrics, files

Coder:
- ONLY for writing Python code
- Writes full runnable code
- Creates files using open() if needed
- NEVER used for planning or analysis

Critic:
- Reviews output and finds gaps
- Must depend on main producer (Coder or Analyst)

Optimizer:
- Improves output after Critic
- Use ONLY if improvement is needed

Validator:
- Final correctness check
- Depends on previous agents

Reporter:
- Writes final structured output
- ALWAYS last agent

----------------------------------------
STRICT ROUTING RULES

1. Planning / Strategy / App Idea:
→ Use: Researcher → Analyst → Critic → Validator → Reporter
→ DO NOT include Coder

2. Coding / Software / Backend:
→ Use: Researcher → Coder → Critic → Optimizer → Validator → Reporter

3. Data / CSV / Analysis:
→ Use: Analyst → Critic → Validator → Reporter
→ Do NOT include Coder

4. Simple Questions:
→ Use minimal agents (2–3 max)

----------------------------------------
CRITICAL RULES (MUST FOLLOW)

- Each agent appears ONLY ONCE
- ALWAYS end with Reporter
- ONLY include required agents (no extras)
- At least one agent MUST have depends_on = []
- NO circular dependencies
- Dependencies must follow logical order

----------------------------------------
DEPENDENCY GUIDELINES

- Researcher → []
- Analyst → [Researcher] (if planning)
- Coder → [Researcher]
- Critic → [Coder or Analyst]
- Optimizer → [Critic]
- Validator → [Critic or Optimizer]
- Reporter → [Validator]

----------------------------------------
OUTPUT FORMAT (STRICT)

Return ONLY JSON:

{
  "steps": [
    {
      "agent": "Researcher",
      "instruction": "Clear, specific instruction",
      "depends_on": []
    }
  ]
}

NO explanation.
NO markdown.
ONLY JSON.
"""


planner_client = LLMClient().client


planner = AssistantAgent(
    name="planner",
    description="Creates structured execution plans for the autonomous agent system",
    system_message=PLANNER_PROMPT,
    model_client=planner_client,
)


async def run_planner(query="plan an ai healthcare startup"):
    result = await planner.run(
        task=TextMessage(
            content=query,
            source="user"
        )
    )

    print(result.messages[-1].content)


# asyncio.run(run_planner())