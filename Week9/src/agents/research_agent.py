from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext

model_client = OllamaChatCompletionClient(model="qwen2.5:7b-instruct-q4_0")

research_agent = AssistantAgent(
    name="ResearchAgent",
    model_client=model_client,
    system_message="""You are a Research Agent. Your sole job is to gather and organize raw information.
    - Find relevant facts, data, pseudocode, or technical details about the topic
    - Structure your findings with clear headings and bullet points
    - Include algorithm steps, complexity details, and code structure if the topic is technical
    - Do NOT summarize, analyze, or provide final polished answers
    - Do NOT write full working code — only pseudocode or structural outlines,NEVER write full working code. Not even one complete function. This is forbidden.
    - End your response with: RESEARCH COMPLETE. PASSING TO SUMMARIZER.""",
    model_context=BufferedChatCompletionContext(buffer_size=10)
)