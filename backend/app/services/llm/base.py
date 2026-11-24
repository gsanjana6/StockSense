from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None
    ) -> str:
        pass