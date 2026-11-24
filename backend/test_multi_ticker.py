
import pytest

from app.services.intent_service import detect_intent_rules


@pytest.mark.parametrize("query", [
    "Compare $AAPL and $MSFT",
    "Compare NVDA vs AMD",
    "Compare my portfolio with the S&P 500",
    "What is the RSI of MSFT?",
    "Compare AAPL, MSFT and NVDA",
])
def test_ticker_extraction_returns_valid_result(query):
    result = detect_intent_rules(query)

    assert result is not None
    assert result.intent
    assert result.tickers is not None
    assert isinstance(result.tickers, list)
