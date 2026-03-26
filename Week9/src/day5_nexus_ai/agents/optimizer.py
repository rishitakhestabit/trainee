from autogen_agentchat.agents import AssistantAgent
from loader import LLMClient
from agent_tools import get_optimizer_tools
from autogen_agentchat.messages import TextMessage
import asyncio


OPTIMIZER_PROMPT = """
You are the Optimizer Agent in an autonomous multi-agent AI system.

ROLE
Improve performance, efficiency, scalability, and resource utilization of existing outputs.

RESPONSIBILITIES
- Detect algorithmic or architectural bottlenecks
- Improve runtime performance and memory usage
- Optimize system scalability and infrastructure usage
- Reduce unnecessary complexity where possible

OPTIMIZATION GUIDELINES
- Prioritize improvements that provide significant gains
- Prefer simple optimizations before complex redesigns
- Quantify improvements where possible
- Clearly document trade-offs or risks introduced

OUTPUT REQUIREMENTS
- Provide an optimized version or description of improvements
- Ensure changes remain maintainable and reliable
"""


optimizer_client = LLMClient().client


optimizer = AssistantAgent(
    name="optimizer",
    description="Improves system performance, efficiency, and scalability",
    system_message=OPTIMIZER_PROMPT,
    model_client=optimizer_client,
    tools=None,
    reflect_on_tool_use=False,
    max_tool_iterations=15
)


async def run_optimizer(query="Inspect generated files and improve performance if needed"):

    result = await optimizer.run(
        task=TextMessage(
            content=query,
            source="user"
        )
    )

    print(result.messages[-1].content)


# asyncio.run(run_optimizer())