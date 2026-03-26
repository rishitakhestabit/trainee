import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient


load_dotenv()


def get_model_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file")

    return OpenAIChatCompletionClient(
        model="llama-3.1-8b-instant",
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
        temperature=0.7,
        max_tokens=2048,
        model_info={
            "type": "openai",
            "json_output": False,
            "vision": False,
            "function_calling": False,
            "structured_output": False,
            "family": "llama",
        },
    )