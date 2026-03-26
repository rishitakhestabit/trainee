from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "Output"
LOG_DIR = BASE_DIR / "logs"

OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE_PATH = LOG_DIR / "nexus-ai.log"

MAX_RETRIES_PER_AGENT = 1
MAX_PLAN_RETRIES = 1