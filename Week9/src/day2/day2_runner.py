import asyncio
import logging
import os
import sys
from datetime import datetime

from utils.model_client import get_model_client
from autogen_core import SingleThreadedAgentRuntime, AgentId
from orchestrator.planner import PlannerAgent
from orchestrator.messages import UserTask
from worker_agent import WorkerAgent
from reflection_agent import ReflectionAgent
from validator import ValidatorAgent

# ── Path Fix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Logging Setup (kept, simplified)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
logs_dir = os.path.join(project_root, "logs", "day2")
os.makedirs(logs_dir, exist_ok=True)

log_filename = os.path.join(
    logs_dir, f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler(log_filename)]
)
logger = logging.getLogger(__name__)


# ── Pipeline
async def run_day2_pipeline(query: str) -> str:
    logger.info(f"QUERY: {query}")

    model_client = get_model_client()
    runtime = SingleThreadedAgentRuntime()

    # register agents
    await WorkerAgent.register(runtime, type="worker", factory=lambda: WorkerAgent(model_client))
    await ReflectionAgent.register(runtime, type="reflection", factory=lambda: ReflectionAgent(model_client))
    await ValidatorAgent.register(runtime, type="validator", factory=lambda: ValidatorAgent(model_client))
    await PlannerAgent.register(runtime, type="planner", factory=lambda: PlannerAgent(model_client, num_workers=3))

    runtime.start()

    planner_id = AgentId("planner", "main")
    result = await runtime.send_message(UserTask(task=query), planner_id)

    # ── Execution Tree (simplified)
    print("\nEXECUTION TREE:")
    print("  Planner")
    print("   ├── Worker-1")
    print("   ├── Worker-2")
    print("   ├── Worker-3")
    print("   └── Reflection")
    print("        └── Validator\n")

    # ── Final Output
    print("FINAL ANSWER:\n")
    print(result.result)
    print("\n" + "-" * 50 + "\n")

    # ── Logs
    logger.info(f"Validation: {'PASS' if result.validation_status else 'FAIL'}")
    logger.info(f"Answer: {result.result}")

    await runtime.stop()
    return result.result


# ── CLI Loop
async def main():
    print("\n" + "=" * 60)
    print("DAY 2 — MULTI-AGENT PIPELINE (type 'exit' to quit)")
    print("=" * 60 + "\n")

    while True:
        query = input("You: ").strip()

        if not query:
            continue

        if query.lower() in ("exit", "quit", "q"):
            print(f"\nLogs saved to: {logs_dir}")
            break

        await run_day2_pipeline(query)


if __name__ == "__main__":
    asyncio.run(main())