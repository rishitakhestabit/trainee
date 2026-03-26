import asyncio
import logging
import os
import sys
from datetime import datetime

# ── Path Fix ──────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autogen_core import SingleThreadedAgentRuntime, AgentId
from autogen_ext.models.ollama import OllamaChatCompletionClient

from orchestrator.planner import PlannerAgent
from orchestrator.messages import UserTask
from worker_agent import WorkerAgent
from reflection_agent import ReflectionAgent
from validator import ValidatorAgent


# ── Suppress noisy AutoGen internal logs ──────────────────────
for _noisy in [
    "autogen_core",
    "autogen_core._single_threaded_agent_runtime",
    "autogen_core._base_agent",
    "autogen_core._routed_agent",
    "autogen_ext.models.ollama",
    "httpx",
    "httpcore",
]:
    logging.getLogger(_noisy).setLevel(logging.WARNING)


# ── Logging Setup ─────────────────────────────────────────────
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
logs_dir = os.path.join(project_root, "logs", "day2")
os.makedirs(logs_dir, exist_ok=True)

log_filename = os.path.join(logs_dir, f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ── Pipeline ──────────────────────────────────────────────────
async def run_day2_pipeline(query: str) -> str:
    logger.info("=" * 60)
    logger.info("DAY 2 PIPELINE STARTED")
    logger.info(f"USER QUERY: {query}")
    logger.info("=" * 60)

    model_client = OllamaChatCompletionClient(model="qwen2.5:7b-instruct-q4_0")
    runtime = SingleThreadedAgentRuntime()

    await WorkerAgent.register(runtime, type="worker", factory=lambda: WorkerAgent(model_client))
    await ReflectionAgent.register(runtime, type="reflection", factory=lambda: ReflectionAgent(model_client))
    await ValidatorAgent.register(runtime, type="validator", factory=lambda: ValidatorAgent(model_client))
    await PlannerAgent.register(runtime, type="planner", factory=lambda: PlannerAgent(model_client, num_workers=3))

    runtime.start()

    try:
        planner_id = AgentId("planner", "main")

        logger.info("ORCHESTRATOR → decomposing task into steps...")
        result = await runtime.send_message(UserTask(task=query), planner_id)

        # ── Execution Tree ─────────────────────────────────────
        print("\nEXECUTION TREE:")
        print("  [Orchestrator / Planner]")
        if hasattr(result, "steps") and result.steps:
            for i, step in enumerate(result.steps, 1):
                marker = "└──" if i == len(result.steps) else "├──"
                print(f"  {marker} Worker-{i}: {step}")
        else:
            for i in range(1, 4):
                marker = "└──" if i == 3 else "├──"
                print(f"  {marker} Worker-{i}: processed subtask")
        print("       └── [Reflection Agent]")
        print("            └── [Validator]")
        print()

        logger.info(f"WORKER AGENTS → {getattr(result, 'num_workers', 3)} workers ran in parallel")
        logger.info("REFLECTION AGENT → answer reviewed and improved")
        logger.info(f"VALIDATOR → {'PASS' if result.validation_status else 'FAIL'}")

        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info(f"Validation: {'PASS' if result.validation_status else 'FAIL'}")
        logger.info(f"FINAL ANSWER:\n{result.result}")
        logger.info("=" * 60)

        print(f"\n{'='*30}")
        print("FINAL ANSWER:")
        print(f"{'='*30}")
        print(result.result)
        print(f"{'='*30}\n")

        return result.result

    except Exception as e:
        logger.error(f"Pipeline FAILED: {e}")
        raise
    finally:
        await runtime.stop()


# ── Continuous Conversation Loop ───────────────────────────────
async def main():
    print("\n" + "=" * 60)
    print("  DAY 2 — MULTI-AGENT ORCHESTRATION PIPELINE")
    print("  Type 'exit' to quit")
    print("=" * 60 + "\n")

    while True:
        query = input("You: ").strip()

        if not query:
            print("  [!] Please enter a query.\n")
            continue

        if query.lower() in ("exit", "quit", "q"):
            print(f"\n  Goodbye! Logs saved to: {logs_dir}")
            break

        await run_day2_pipeline(query)
        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())