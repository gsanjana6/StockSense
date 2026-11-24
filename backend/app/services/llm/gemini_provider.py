import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.services.llm.base import LLMProvider


load_dotenv()


class GeminiProvider(LLMProvider):

    def __init__(self, model_name: str):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing from the backend .env file."
            )

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None
    ) -> str:

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
                max_output_tokens=1500
            )
        )

        text = response.text

        if not text or not text.strip():
            raise ValueError("The AI provider returned an empty response.")

        return text.strip()