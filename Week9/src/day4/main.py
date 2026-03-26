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
model_client = OpenAIChatCompletionClient(
    model="openai/gpt-oss-20b",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
    model_info={
        "family": "openai",
        "context_length": 8192,
        "function_calling": True,
        "vision": False,
        "json_output": False,
        "structured_output": True
    }
)

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

        start_time = time.time()  #  start timer

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

        print(f"\nAGENT: {answer}")  #  clean terminal output

        memory.store_interaction(user_input, answer)

        end_time = time.time()  # ⏱ end timer
        duration = end_time - start_time

        # Save logs (with timestamp, hidden from terminal)
        write_log(user_input, answer, duration)


if __name__ == "__main__":
    asyncio.run(ask_agent())