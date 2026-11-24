
from app.services.llm.response_verification_service import (
    verify_llm_response
)


def test_correlation_response_verification():
    context = {
        "correlation": {
            "period": "1y",
            "matrix": {
                "AAPL": {
                    "AAPL": 1.0,
                    "MSFT": 0.75
                },
                "MSFT": {
                    "AAPL": 0.75,
                    "MSFT": 1.0
                }
            }
        }
    }

    response = (
        "Over the 1-year period, AAPL and MSFT "
        "have a correlation of 0.75. "
        "This indicates a positive relationship "
        "between their historical returns."
    )

    result = verify_llm_response(
        response=response,
        context=context
    )

    assert result["status"] == "passed"
