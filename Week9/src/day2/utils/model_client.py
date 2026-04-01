import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

def get_model_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file")

    return OpenAIChatCompletionClient(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        api_key=api_key,
        base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        temperature=0.3,
        max_tokens=1500,
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": "unknown",
        },
    )