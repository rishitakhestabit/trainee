from autogen_core import RoutedAgent, MessageContext, message_handler
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage
from orchestrator.messages import WorkerTask, WorkerResult


class WorkerAgent(RoutedAgent):
    """Worker Agent - Handles individual subtasks independently."""

    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(description="Worker Agent - Task Processor")
        self._model_client = model_client

    @message_handler
    async def handle_task(self, message: WorkerTask, ctx: MessageContext) -> WorkerResult:
        """
        Processes a single subtask assigned by the Planner.
        Worker focuses ONLY on execution (no synthesis).
        """

        # ── Worker Execution Mode ──────────────────────────────
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

        # ── LLM Call ───────────────────────────────────────────
        model_result = await self._model_client.create(messages)
        result = str(model_result.content)

        # ── Debug Output ───────────────────────────────────────
        print(f"\n{'='*80}")
        print(f"Worker-{self.id.key} (Subtask: {message.subtask_id})")
        print(f"{'-'*80}")
        print(f"{result[:200]}...")
        print(f"{'='*80}\n")

        # ── Return Result ──────────────────────────────────────
        return WorkerResult(
            subtask_id=message.subtask_id,
            result=result,
            agent_id=str(self.id)
        )