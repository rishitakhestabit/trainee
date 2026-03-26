from autogen_agentchat.agents import AssistantAgent
from loader import LLMClient
from autogen_agentchat.messages import TextMessage
from agent_tools import get_analyst_tools
import asyncio


ANALYST_PROMPT = """
You are the Analyst Agent in an autonomous multi-agent AI system.

ROLE
Analyze datasets and convert raw information into actionable business insights.

TOOL USAGE RULES — FOLLOW STRICTLY
- ONLY call tools if the task explicitly mentions a filename (e.g. sales.csv)
- If a filename is mentioned → call get_csv_summary with that exact filename FIRST
- If NO filename is mentioned → do NOT call any tools, provide analysis from context only
- NEVER guess or invent a filename
- NEVER call read_csv, read_file, or list_directory unless a path is explicitly given

RESPONSIBILITIES
- If a CSV file is provided: use get_csv_summary to analyze it, then extract business insights
- If no file is provided: analyze market trends, competitive landscape, and business strategy from context
- Detect trends, patterns, and opportunities
- Quantify insights using metrics and evidence where possible

OUTPUT REQUIREMENTS
- Provide clear insights tied to business impact
- Include prioritized recommendations
- Highlight risks and opportunities
- Distinguish facts from assumptions
- Be concise but complete
"""


analyst_client = LLMClient().client


analyst = AssistantAgent(
    name="analyst",
    description="Analyzes datasets and market trends to extract business insights and strategic recommendations",
    system_message=ANALYST_PROMPT,
    model_client=analyst_client,
    tools=get_analyst_tools(),
    reflect_on_tool_use=True,
    max_tool_iterations=10,
)


async def run_analyst(query="Analyze sales.csv and provide a concise business summary with key metrics and recommendations."):

    result = await analyst.run(
        task=TextMessage(
            content=query,
            source="user"
        )
    )

    print(result.messages[-1].content)


# asyncio.run(run_analyst())