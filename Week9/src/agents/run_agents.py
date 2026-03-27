import asyncio
import logging
import os
import sys
from datetime import datetime

# ── Path Fix ──────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from research_agent import research_agent
from summarizer_agent import summarizer_agent
from answer_agent import answer_agent

# ── Logging Setup ─────────────────────────────────────────────
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
logs_dir = os.path.join(project_root, "logs")
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
async def run_pipeline(query: str) -> str:
    logger.info("=" * 60)
    logger.info("PIPELINE STARTED")
    logger.info(f"USER QUERY: {query}")
    logger.info("=" * 60)

    # Step 1: Research Agent
    try:
        logger.info("[1/3] Research Agent started")
        research_response = await research_agent.run(task=query)
        research_result = research_response.messages[-1].content
        logger.info("[1/3] Research Agent completed successfully")
        logger.info(f"RESEARCH OUTPUT:\n{research_result}\n")
    except Exception as e:
        logger.error(f"[1/3] Research Agent FAILED: {e}")
        return ""

    # Step 2: Summarizer Agent
    try:
        logger.info("[2/3] Summarizer Agent started")
        summary_response = await summarizer_agent.run(task=research_result)
        summary_result = summary_response.messages[-1].content
        logger.info("[2/3] Summarizer Agent completed successfully")
        logger.info(f"SUMMARY OUTPUT:\n{summary_result}\n")
        
    except Exception as e:
        logger.error(f"[2/3] Summarizer Agent FAILED: {e}")
        return ""

    # Step 3: Answer Agent
    try:
        logger.info("[3/3] Answer Agent started")
        answer_response = await answer_agent.run(task=summary_result)
        answer_result = answer_response.messages[-1].content
        logger.info("[3/3] Answer Agent completed successfully")
        logger.info(f"FINAL ANSWER:\n{answer_result}\n")
    except Exception as e:
        logger.error(f"[3/3] Answer Agent FAILED: {e}")
        return ""

    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info(f"Log saved to: {log_filename}")
    logger.info("=" * 60)

    return answer_result


# ── Continuous Conversation Loop 
async def main():
    print("\n" + "=" * 60)
    print("  NEXUS AGENT PIPELINE — Type 'exit' to quit")
    print("=" * 60 + "\n")

    while True:
        query = input("You: ").strip()

        if not query:
            print("  [!] Please enter a query.\n")
            continue

        if query.lower() in ("exit", "quit", "q"):
            print("\n  Goodbye! All logs saved to:", logs_dir)
            break

        await run_pipeline(query)
        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())