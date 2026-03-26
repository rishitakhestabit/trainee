import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

class LLMClient:
    def __init__(self, response_structure=None):
        api_key = os.getenv("GROQ_API_KEY")
        base_url = os.getenv("GROQ_BASE_URL")
        model = os.getenv("GROQ_MODEL")

        if not api_key:
            raise RuntimeError("Missing GROQ_API_KEY.")
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
                "structured_output": False,
            },
        )
