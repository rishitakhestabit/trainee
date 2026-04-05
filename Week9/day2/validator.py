from autogen_core import RoutedAgent, MessageContext, message_handler
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage
from orchestrator.messages import ValidationTask, ValidationResult


class ValidatorAgent(RoutedAgent):

    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(description="Validator Agent - Quality Assurance")
        self._model_client = model_client

    @message_handler
    async def handle_task(self, message: ValidationTask, ctx: MessageContext) -> ValidationResult:
        system_prompt = (
            "You are a Validator Agent. Check the result and respond in EXACTLY this format:\n"
            "VALIDATION: PASS\n"
            "or\n"
            "VALIDATION: FAIL\n"
            "ERRORS: [errors or 'None']\n"
            "FINAL_RESULT: [approved result]\n"
        )

        messages = [
            SystemMessage(content=system_prompt),
            UserMessage(
                content=(
                    f"Original Task:\n{message.original_task}\n\n"
                    # Truncate reflected result to 800 chars to reduce context
                    f"Result to Validate:\n{message.reflected_result[:800]}\n\n"
                    f"Validate and respond in the required format."
                ),
                source="user"
            )
        ]

    
        model_result = await self._model_client.create(messages)
        validation_text = str(model_result.content)

        is_valid = "VALIDATION: PASS" in validation_text

        print(f"\n{'='*80}")

        print(f"Validation Status: {'PASS' if is_valid else 'FAIL'}")
        print(f"{'='*80}\n")

        return ValidationResult(
            is_valid=is_valid,
            final_result=message.reflected_result
        )