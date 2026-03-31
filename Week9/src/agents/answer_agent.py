from autogen_agentchat.agents import AssistantAgent
# from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext
from utils.model_client import get_model_client
# model_client = OllamaChatCompletionClient(model="qwen2.5:7b-instruct-q4_0")


answer_agent = AssistantAgent(
    name="AnswerAgent",
    model_client=get_model_client(),
    system_message="""You are an Answer Agent. Your sole job is to produce the final, complete answer for the user.

    STRICT RULES — VIOLATING THESE IS A FAILURE:
    1. Use ONLY the summary provided to you as your source of truth
    2. NEVER introduce facts, names, events, or details not present in the summary — this is hallucination and is forbidden
    3. If the summary does not mention a specific festival, person, or event name — do NOT invent one
    4. Do NOT say "based on the summary" — speak directly to the user
    5. For conceptual or theoretical questions:
    - Provide clear and simple explanation
    - Use examples if helpful
    - Do NOT include code or pseudocode
    Only include code if the user explicitly asks for:
    - "write code"
    - "implement"
    - "example in Python"
    6. For non-technical topics: provide clear actionable steps or recommendations
    7. This is the last step — make your answer self-contained, polished, and accurate""",
    model_context=BufferedChatCompletionContext(buffer_size=10)
)