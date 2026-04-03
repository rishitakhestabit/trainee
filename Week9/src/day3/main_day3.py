import asyncio
from orchestrator.orchestrator import Orchestrator
import logging
import os
from datetime import datetime

# ── Logging Setup ─────────────────────────────
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
logs_dir = os.path.join(project_root, "logs", "day3")
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

async def main():
    orch = Orchestrator()
    print("Agentic Data Assistant - type 'exit' to quit\n")

    while True:
        try:
            q = input("You: ").strip()

            if not q or q.lower() in ("exit", "quit"):
                print(f"\nLogs saved to: {logs_dir}")
                break

            logger.info(f"USER QUERY: {q}")   

            res = await orch.run(q)

            logger.info(f"RESULT: {res}")     

            print(f"\n{res}\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"ERROR: {e}")   
            print(f"\nUnexpected error: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())