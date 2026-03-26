from autogen_agentchat.agents import AssistantAgent
from loader import LLMClient
from pydantic import BaseModel
from typing import List


class CritiqueReport(BaseModel):
    issues_found: List[str]
    severity_levels: List[str]
    edge_cases: List[str]
    improvement_suggestions: List[str]
    overall_assessment: str


CRITIC_PROMPT = """
You are the Critic Agent in an autonomous multi-agent AI system.

ROLE
Evaluate outputs from other agents and identify weaknesses, risks, and potential failures.

RESPONSIBILITIES
- Detect logical gaps or incorrect assumptions
- Identify risks related to security, scalability, performance, or maintainability
- Highlight missing requirements or incomplete reasoning
- Identify edge cases and failure scenarios

REVIEW STANDARDS
- Prioritize issues by severity: Critical, High, Medium, Low
- Explain the impact of each issue
- Provide clear improvement suggestions
- Focus on meaningful risks instead of minor stylistic issues

OUTPUT REQUIREMENTS
Return a structured critique including:
- issues_found
- severity_levels
- edge_cases
- improvement_suggestions
- overall_assessment
"""


critic_client = LLMClient().client


critic = AssistantAgent(
    name="critic",
    description="Reviews solutions and identifies flaws, risks, and edge cases",
    system_message=CRITIC_PROMPT,
    model_client=critic_client,
)