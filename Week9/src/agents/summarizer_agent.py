from autogen_agentchat.agents import AssistantAgent
# from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext

# model_client = OllamaChatCompletionClient(model="qwen2.5:7b-instruct-q4_0")
from utils.model_client import get_model_client

summarizer_agent = AssistantAgent(
    name="SummarizerAgent",
    model_client=get_model_client(),
    system_message="""You are a Summarizer Agent. Your sole job is to condense raw research into a tight summary.
    - Read the research provided carefully
    - Write a concise summary of 1-2 paragraphs covering all key points
    - Preserve important technical details, steps, and complexity info
    - Do NOT write final answers, working code, or actionable recommendations
    - Do NOT add new information not present in the research
    - End your response with: SUMMARY COMPLETE. PASSING TO ANSWER AGENT.""",
    model_context=BufferedChatCompletionContext(buffer_size=10)
)