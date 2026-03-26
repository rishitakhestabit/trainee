from autogen_agentchat.agents import AssistantAgent
from loader import LLMClient
from pydantic import BaseModel
from typing import List


class ResearchFindings(BaseModel):
    sources: List[str]
    key_facts: List[str]
    summary: str
    confidence_level: str


RESEARCHER_PROMPT = """
You are the Researcher Agent in an autonomous multi-agent system.

ROLE
Gather reliable information and structured research to support downstream agents.

RESPONSIBILITIES
- Identify important research topics from the task
- Gather relevant domain knowledge, standards, and best practices
- Prefer credible and authoritative information
- Highlight uncertainties if knowledge is incomplete

OUTPUT REQUIREMENTS
Return structured findings including:
- key_facts
- sources
- concise summary
- confidence_level

Keep the output structured and useful for other agents.
"""


researcher_client = LLMClient().client


researcher = AssistantAgent(
    name="researcher",
    description="Collects factual information and domain knowledge for the system",
    system_message=RESEARCHER_PROMPT,
    model_client=researcher_client,
)