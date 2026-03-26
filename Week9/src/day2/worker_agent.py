from autogen_core import RoutedAgent, MessageContext, message_handler
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage
from orchestrator.messages import WorkerTask, WorkerResult


class WorkerAgent(RoutedAgent):
    """RoutedAgent + message_handler for AutoGen's automatic message dispatch."""

    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(description="Worker Agent - Task Processor")
        self._model_client = model_client

    @message_handler
    async def handle_task(self, message: WorkerTask, ctx: MessageContext) -> WorkerResult:

        if message.previous_results:
            # Synthesis mode: combine previous layer outputs
            system_prompt = (
                "You are a synthesis agent. "
                "You have been provided with responses from previous agents. "
                "Your task is to synthesize these into a single, high-quality response. "
                "Critically evaluate the information, recognizing biases or errors. "
                "Provide a refined, accurate, and comprehensive answer.\n\n"
                "Previous responses:\n"
            )
            system_prompt += "\n".join(
                [f"{i+1}. {result}" for i, result in enumerate(message.previous_results)]
            )
            messages = [
                SystemMessage(content=system_prompt),
                UserMessage(content=message.task, source="user")
            ]

        else:
            # Fresh processing mode: include original task as context so workers
            # never lose sight of the full query (fixes "could you specify?" issue)
            system_prompt = (
                "You are a worker agent specialized in processing tasks independently. "
                "Provide clear, accurate, and detailed responses. "
                "Focus ONLY on the specific subtask assigned to you.\n\n"
                f"IMPORTANT CONTEXT — Full original task: {message.original_task}\n"
                "Use this context to give a specific, complete answer. "
                "Do NOT ask clarifying questions. Just answer directly."
            )
            messages = [
                SystemMessage(content=system_prompt),
                UserMessage(content=message.task, source="user")
            ]

        model_result = await self._model_client.create(messages)
        result = str(model_result.content)

        print(f"\n{'='*80}")
        print(f"Worker-{self.id.key} (Subtask: {message.subtask_id})")
        print(f"{'-'*80}")
        print(f"{result[:200]}...")
        print(f"{'='*80}\n")

        return WorkerResult(
            subtask_id=message.subtask_id,
            result=result,
            agent_id=str(self.id)
        )