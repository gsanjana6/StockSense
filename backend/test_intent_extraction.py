
import pytest

from app.services.intent_service import detect_intent_rules


@pytest.mark.parametrize("query", [
    "Show me my portfolio summary",
    "Compare my portfolio performance with the S&P 500",
    "What is the RSI of MSFT?",
    "Explain what the Sharpe ratio means",
    "Calculate my portfolio Sharpe ratio",
    "What is the weather today?",
    "Show me the current stock price of $AAPL",
    "Explain diversification",
    "What if I add 10 shares of MSFT?",
    "Tell me about Microsoft",
])
def test_intent_classification_returns_valid_result(query):
    result = detect_intent_rules(query)

    assert result is not None
    assert result.intent
    assert 0 <= result.confidence <= 1
