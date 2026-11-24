import logging
import socket

from app.services.llm.gemini_provider import GeminiProvider


logger = logging.getLogger(__name__)


def classify_provider_error(error: Exception):
    """
    Identify errors that justify trying another provider.
    """

    status = (
        getattr(error, "status_code", None)
        or getattr(error, "code", None)
    )

    message = str(error).lower()

    if status == 429 or "429" in message or "resource_exhausted" in message:
        return "rate_limit"

    if (
        isinstance(error, (TimeoutError, socket.timeout))
        or "timeout" in message
        or "timed out" in message
    ):
        return "timeout"

    if (
        isinstance(status, int) and 500 <= status < 600
    ) or any(code in message for code in ["500", "502", "503", "504"]):
        return "server_error"

    if status in (400, 401, 403) or any(
        phrase in message
        for phrase in [
            "invalid api key",
            "permission denied",
            "unauthorized",
            "bad request"
        ]
    ):
        return "configuration_or_request_error"

    return "unknown_error"


class ProviderManager:

    def __init__(self):

        # Primary and explanation fallback models.
        self.primary = GeminiProvider(
            "gemini-3.5-flash-lite"
        )

        self.secondary = GeminiProvider(
            "gemini-3.1-flash-lite"
        )

        self.tertiary = GeminiProvider(
            "gemma-4-31b-it"
        )

        # Separate model for intent/parameter extraction fallback.
        self.intent_fallback = GeminiProvider(
            "gemma-4-26b-a4b-it"
        )

    def generate_with_fallback(
        self,
        prompt: str,
        system_instruction: str | None = None,
        intent_task: bool = False
    ) -> dict:

        if intent_task:
            providers = [
                ("gemma-4-26b-a4b-it", self.intent_fallback)
            ]
        else:
            providers = [
                ("gemini-3.5-flash-lite", self.primary),
                ("gemini-3.1-flash-lite", self.secondary),
                ("gemma-4-31b-it", self.tertiary)
            ]

        for model_name, provider in providers:

            try:
                result = provider.generate(
                    prompt=prompt,
                    system_instruction=system_instruction
                )

                return {
                    "success": True,
                    "model": model_name,
                    "response": result,
                    "error": None
                }

            except Exception as error:

                error_type = classify_provider_error(error)

                logger.warning(
                    "Provider %s failed: %s (%s)",
                    model_name,
                    error,
                    error_type
                )

                # Do not keep retrying configuration or programming errors.
                if error_type in [
                    "configuration_or_request_error",
                    "unknown_error"
                ]:
                    break

        return {
            "success": False,
            "model": None,
            "response": None,
            "error": "All available AI provider attempts failed."
        }