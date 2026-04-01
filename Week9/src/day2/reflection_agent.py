from autogen_core import RoutedAgent, MessageContext, message_handler
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage
from orchestrator.messages import ReflectionTask, ReflectionResult


class ReflectionAgent(RoutedAgent):
    """Reflection agent that synthesizes multiple worker results
    and improves quality through critical evaluation."""

    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(description="Reflection Agent - Quality Improvement")
        self._model_client = model_client

    @message_handler
    async def handle_task(self, message: ReflectionTask, ctx: MessageContext) -> ReflectionResult:
        MAX_LEN = 1500
        # Truncate each worker result to 500 chars to reduce context size
        combined = "\n\n".join([
            f"--- Worker {i+1} (Subtask: {wr.subtask_id}) ---\n{wr.result[:MAX_LEN]}"
            for i, wr in enumerate(message.worker_results)
        ])

        prompt = (
            "You are a Reflection Agent. Synthesize the worker outputs into one concise, accurate final answer.\n"
            "Be brief. No repetition. Max 300 words.\n\n"
            "Worker outputs:\n"
            + combined
        )

        messages = [
            SystemMessage(content=prompt),
            UserMessage(
                content=f"Original task: {message.original_task}\n\nSynthesize the above into a final answer.",
                source="user"
            )
        ]

        # Cap output to 400 tokens to prevent long generation
        model_result = await self._model_client.create(messages)
        result_text = str(model_result.content)
        print(f"{result_text[:300]}...")
        print(f"{'='*80}\n")

        return ReflectionResult(refined_result=result_text)