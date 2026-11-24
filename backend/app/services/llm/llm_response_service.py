
import json
import logging

from app.services.llm.provider_manager import ProviderManager

logger = logging.getLogger(__name__)

_provider_manager = None


def get_provider_manager():
    global _provider_manager

    if _provider_manager is None:
        _provider_manager = ProviderManager()

    return _provider_manager


SYSTEM_INSTRUCTION = """
You are StockSense, an AI-powered financial analytics assistant.

Your responsibilities:
- Answer financial and investment-related questions clearly.
- Explain financial concepts using your own knowledge.
- Interpret market data and portfolio analytics supplied to you.
- Explain financial metrics and what they mean.
- Identify portfolio strengths, weaknesses and potential areas
  for improvement using the supplied data.
- Compare stocks using the supplied figures.

Important rules:
1. Never invent stock prices, financial figures or portfolio metrics.
2. Treat supplied financial data as the source of truth.
3. If required data is missing, clearly state that.
4. Distinguish historical performance from future expectations.
5. Do not claim to have fetched live data unless it was supplied.
6. Do not guarantee investment returns.
7. Explain technical financial terminology in understandable language.
8. Provide reasoning for your conclusions.
9. Do not fabricate portfolio holdings or user information.
10. Do not execute trades or claim to provide personalised
    regulated investment advice.

Respond naturally and directly to the user's question.
"""


def generate_chat_response(
    message: str,
    context: dict | None = None
) -> dict:

    context = context or {}

    prompt = f"""
USER QUESTION:
{message}

AVAILABLE STOCKSENSE DATA:
{json.dumps(context, indent=2, default=str)}

INSTRUCTIONS:
Answer the user's question using your financial knowledge
and the supplied StockSense data where relevant.

If the question is conceptual, answer using your own knowledge.
If it requires market or portfolio data that is not supplied,
do not guess or fabricate it.
"""

    try:
        manager = get_provider_manager()

        result = manager.generate_with_fallback(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION
        )

        if not result.get("success"):
            return {
                "success": False,
                "response": None,
                "model": None,
                "error": result.get("error")
            }

        response = result.get("response")

        if not response or not response.strip():
            return {
                "success": False,
                "response": None,
                "model": result.get("model"),
                "error": "The AI returned an empty response."
            }

        return {
            "success": True,
            "response": response.strip(),
            "model": result.get("model"),
            "error": None
        }

    except Exception as error:
        logger.exception("LLM response generation failed")

        return {
            "success": False,
            "response": None,
            "model": None,
            "error": str(error)
        }
