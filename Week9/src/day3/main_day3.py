import os
import asyncio
import logging
from datetime import datetime
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from orchestrator.orchestrator import Orchestrator
from utils.model_client import get_model_client

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs", "day3"))


def setup_logger():
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"day3_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
    logger = logging.getLogger("day3_runner")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    logger.addHandler(handler)
    return logger


summarizer = AssistantAgent(
    name="Summarizer",
    model_client=get_model_client(),
    system_message=(
        "You are a result narrator.\n"
        "You are given a user's question and the exact output that was produced.\n"
        "Write 1-2 sentences that describe what the output shows — using only "
        "the facts present in the output.\n"
        "Rules:\n"
        "- Do NOT mention code, Python, loops, functions, or any implementation detail.\n"
        "- Do NOT infer or guess anything not visible in the output.\n"
        "- Do NOT use bullet points or markdown.\n"
        "- Speak about the data/results only.\n"
    ),
)


async def get_summary(user_query: str, result: str) -> str:
    response = await summarizer.on_messages(
        [TextMessage(
            content=f"Question: {user_query}\nOutput:\n{result}",
            source="user",
        )],
        cancellation_token=None,
    )
    return response.chat_message.content.strip()


async def run_task(user_query: str, logger: logging.Logger, orchestrator: Orchestrator):
    try:
        result = await orchestrator.process_request(
            user_query,
            status_callback=lambda msg: logger.info("STATUS: %s", msg),
        )

        # Trust final_answer from orchestrator.synthesize_results() directly.
        # Re-extracting from agent_results here would bypass the orchestrator's
        # wants_code logic and always return execution_result instead of generated_code.
        final_answer = result.get("final_answer", "").strip()

        summary = await get_summary(user_query, final_answer)

        print("\n" + "=" * 80)
        print("RESULT")
        print("=" * 80)
        print(final_answer)
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(summary)
        print("=" * 80 + "\n")

        logger.info("QUERY: %s", user_query)
        logger.info("RESULT:\n%s", final_answer)
        logger.info("SUMMARY: %s", summary)

    except Exception as e:
        logger.exception("Runner failed for query: %s", user_query)
        print(f"Error: {e}")


def main():
    logger       = setup_logger()
    orchestrator = Orchestrator(database_path="sales.db")

    print("Day 3 runner started. Type your task below.")
    print("Type 'exit' to quit.")

    while True:
        user_query = input("\n> ").strip()
        if not user_query:
            print("Please enter a task or type 'exit'.")
            continue
        if user_query.lower() == "exit":
            print("Exiting Day 3 runner.")
            break
        asyncio.run(run_task(user_query, logger, orchestrator))


if __name__ == "__main__":
    main()