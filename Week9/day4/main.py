import asyncio
import os
import time
from datetime import datetime
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from memory.memory_manager import MemoryManager

load_dotenv()

# -------------------- LLM CLIENT --------------------
class LLMClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        base_url = os.getenv("GROQ_BASE_URL")
        model = os.getenv("GROQ_MODEL")

        if not api_key:
            raise RuntimeError("Missing GROQ_API_KEY.")
        if not base_url:
            raise RuntimeError("Missing GROQ_BASE_URL.")
        if not model:
            raise RuntimeError("Missing GROQ_MODEL.")

        self.client = OpenAIChatCompletionClient(
            model=model,
            base_url=base_url,
            api_key=api_key,
            model_info={
                "family": "openai",
                "context_length": 8192,
                "function_calling": True,
                "vision": False,
                "json_output": False,
                "structured_output": True,  # keep True for Day 4
            },
        )
# -------------------- LOGGING SETUP --------------------
LOG_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../logs/day4")
)
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "log.txt")


def write_log(user_input, answer, duration):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"""
[{timestamp}]
USER: {user_input}
AGENT: {answer}
TIME_TAKEN: {duration:.2f} seconds
{'-'*60}
"""

    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

# -------------------- MEMORY --------------------
memory = MemoryManager()

# -------------------- MODEL --------------------
llm = LLMClient()
model_client = llm.client

# -------------------- AGENT --------------------
agent = AssistantAgent(
    name="SmartAgent",
    model_client=model_client,
    system_message="""
You are an intelligent assistant with access to long-term memory.

You will receive:
1. Retrieved long-term memories
2. Recent conversation context
3. The user's question

Use memory ONLY if it is relevant to answering the question.

If memory is irrelevant, ignore it and answer normally.
"""
)
# -------------------- MAIN LOOP --------------------
async def ask_agent():

    while True:

        user_input = input("\nEnter your query (type 'exit' to quit): ")

        if user_input.strip().lower() == "exit":
            print("Have a good day !!")
            break

        start_time = time.time()

        context = memory.retrieve_context(user_input)

        message = f"""
        MEMORY CONTEXT:
        {context}

        USER QUESTION:
        {user_input}
        """
        response = await agent.run(
            task=TextMessage(
                content=message,
                source="user"
            )
        )
        answer = response.messages[-1].content
        print(f"\nAGENT: {answer}")
        memory.store_interaction(user_input, answer)
        end_time = time.time()
        duration = end_time - start_time
        write_log(user_input, answer, duration)

if __name__ == "__main__":
    asyncio.run(ask_agent())