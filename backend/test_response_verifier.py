
from app.services.technical_analysis import (
    calculate_technical_analysis
)

from app.services.llm.response_verification_service import (
    verify_llm_response
)

# Get actual AAPL technical analysis data
technical_data = calculate_technical_analysis("AAPL")

# Pass the actual service output to the verifier
context = {
    "technical_analysis": technical_data
}

rsi = technical_data["indicators"]["rsi_14"]
date = technical_data["data_date"]

response = f"""
Based on the supplied data for AAPL as of {date},
the 14-day Relative Strength Index (RSI) is {rsi:.2f}.

What does this mean?

An RSI of {rsi:.2f} falls in the middle of the standard
0 to 100 scale, generally considered a neutral zone
(neither overbought, which is typically above 70,
nor oversold, which is typically below 30).

This metric describes historical price behavior
and does not predict future returns.
"""

print("ACTUAL RSI:", rsi)
print("SOURCE TICKER:", technical_data["ticker"])

result = verify_llm_response(response, context)

print("\nVERIFICATION RESULT:")
print(result)
