
import re

from app.schemas.chat import IntentResult


# --------------------------------------------------
# PERIOD EXTRACTION
# --------------------------------------------------

PERIOD_PATTERNS = {
    "1mo": ["1 month", "one month", "monthly"],
    "3mo": ["3 months", "three months"],
    "6mo": ["6 months", "six months"],
    "1y": ["1 year", "one year", "12 months", "yearly", "annually"],
    "2y": ["2 years", "two years"],
    "5y": ["5 years", "five years"],
}


# --------------------------------------------------
# FINANCIAL CONCEPTS
# --------------------------------------------------

FINANCIAL_CONCEPTS = [
    "sharpe ratio",
    "sortino ratio",
    "alpha",
    "beta",
    "volatility",
    "standard deviation",
    "maximum drawdown",
    "drawdown",
    "dividend",
    "market capitalization",
    "market cap",
    "p/e ratio",
    "price to earnings",
    "earnings per share",
    "eps",
    "roe",
    "roa",
    "moving average",
    "rsi",
    "macd",
    "bollinger bands",
    "portfolio diversification",
    "diversification",
    "asset allocation",
    "correlation",
    "compound annual growth rate",
    "cagr",
    "etf",
    "index fund",
    "stock market",
]


# --------------------------------------------------
# UNSUPPORTED REQUESTS
# --------------------------------------------------

UNSUPPORTED_TOPICS = [
    "weather",
    "temperature today",
    "recipe",
    "football",
    "cricket",
    "movie recommendation",
    "write an essay",
    "translate this",
    "tell me a joke",
]

UNSUPPORTED_FINANCIAL_REQUESTS = [
    "should i buy",
    "should i sell",
    "should i invest",
    "tell me what to buy",
    "tell me what to sell",
    "recommend a stock",
    "recommend stocks",
    "best stock to buy",
    "give me a buy signal",
    "give me a sell signal",
    "predict the stock price",
    "predict the market",
    "price prediction",
    "future stock price",
    "guaranteed returns",
    "execute a trade",
    "place an order",
    "buy shares for me",
    "sell shares for me",
]


# --------------------------------------------------
# COMMON HELPERS
# --------------------------------------------------

def contains_phrase(text: str, phrases: list[str]) -> bool:
    """Match complete phrases without partial-word matches."""

    return any(
        re.search(
            rf"(?<!\w){re.escape(phrase)}(?!\w)",
            text
        )
        for phrase in phrases
    )


# --------------------------------------------------
# PERIOD EXTRACTION
# --------------------------------------------------

def extract_period(message: str):
    text = message.lower()

    for period, phrases in PERIOD_PATTERNS.items():
        if contains_phrase(text, phrases):
            return period

    return None


# --------------------------------------------------
# TICKER EXTRACTION
# --------------------------------------------------

IGNORED_TICKER_WORDS = {
    "I", "A", "S", "P", "SPY", "USD", "INR", "AI", "ETF",
    "RSI", "MACD", "SMA", "EMA", "ATR", "VWAP", "OHLC",
    "PE", "EPS", "ROE", "ROA", "NYSE", "NASDAQ", "USA",
    "US", "UK", "AND", "OR", "THE", "MY", "IS", "IT",
    "FOR", "TO", "OF", "IN", "ON", "VS", "GDP", "CAGR",
}


def extract_multiple_tickers(message: str) -> list[str]:
    """
    Extract possible ticker symbols from a message.

    Supports:
        $AAPL and $MSFT
        AAPL and MSFT
        NVDA vs AMD

    These are candidates only. They must be verified
    against the company database before financial use.
    """

    # Explicitly marked tickers.
    explicit_matches = re.findall(
        r"\$([A-Za-z]{1,10})\b",
        message
    )

    # Standalone uppercase ticker candidates.
    uppercase_matches = re.findall(
        r"\b[A-Z]{2,5}\b",
        message
    )

    tickers = []

    for ticker in explicit_matches + uppercase_matches:
        ticker = ticker.upper()

        if (
            ticker not in IGNORED_TICKER_WORDS
            and ticker not in tickers
        ):
            tickers.append(ticker)

    return tickers


def extract_ticker(message: str):
    """Extract the first ticker candidate for single-stock requests."""

    tickers = extract_multiple_tickers(message)

    return tickers[0] if tickers else None


# --------------------------------------------------
# PREDICTION REQUEST DETECTION
# --------------------------------------------------

def is_prediction_request(text: str) -> bool:

    prediction_patterns = [
        r"\bpredict\b",
        r"\bforecast\b",
        r"\bprice target\b",
        r"\btarget price\b",
        r"\bwill .{1,60} stock .{0,20} (?:rise|fall|increase|decrease)\b",
        r"\bwhere will .{1,60} trade\b",
        r"\bexpected price\b",
    ]

    return any(
        re.search(pattern, text)
        for pattern in prediction_patterns
    )


# --------------------------------------------------
# INTENT CLASSIFICATION
# --------------------------------------------------

def detect_intent_rules(
    message: str,
    portfolio_id: int | None = None
) -> IntentResult:

    text = message.lower().strip()

    # Extract parameters.
    tickers = extract_multiple_tickers(message)
    ticker = tickers[0] if tickers else None
    period = extract_period(message)

    benchmark = (
        "SPY"
        if contains_phrase(
            text,
            ["s&p 500", "sp500", "spy", "benchmark"]
        )
        else None
    )

    intent = "clarification"
    confidence = 0.50

    # 1. Unsupported topics and financial requests.
    if (
        is_prediction_request(text)
        or contains_phrase(text, UNSUPPORTED_TOPICS)
        or contains_phrase(text, UNSUPPORTED_FINANCIAL_REQUESTS)
        or contains_phrase(
            text,
            [
                "cryptocurrency",
                "crypto",
                "bitcoin",
                "ethereum",
                "options trading",
                "forex trading",
            ]
        )
    ):
        intent = "unsupported"
        confidence = 0.99

    # 2. What-if simulations.
    elif contains_phrase(
        text,
        [
            "what if",
            "what-if",
            "what happens if",
            "what would happen if",
            "simulate",
            "simulation",
            "add a stock",
            "add shares",
            "adding shares",
            "added shares",
            "if i add",
            "if i added",
            "remove a stock",
            "remove shares",
            "reduce my holding",
            "increase my holding",
            "what if i buy",
            "what if i sell",
        ]
    ):
        intent = "what_if"
        confidence = 0.95
    # 3. Educational financial concept questions.
    # Classify explanations/definitions as concepts unless
    # the user is asking about a specific stock.

    has_stock_reference = (
        bool(tickers)
        or bool(
            re.search(
                r"\b(?:of|for)\s+[A-Z][a-zA-Z.&-]*",
                message
            )
        )
        or bool(
            re.search(
                r"\b[A-Z][a-zA-Z.&-]*['’]s\b",
                message
            )
        )
    )

    is_educational_question = (
        contains_phrase(
            text,
            [
                "explain",
                "define",
                "meaning of",
                "what does",
                "what is",
                "what are",
                "how does",
            ]
        )
        and contains_phrase(text, FINANCIAL_CONCEPTS)
    )

    if intent in {"what_if", "unsupported"}:
        pass

    elif (
        is_educational_question
        and not has_stock_reference
        and not contains_phrase(
            text,
            [
                "my portfolio",
                "portfolio",
                "my holdings",
                "my investments",
            ]
        )
    ):
        intent = "financial_concept"
        confidence = 0.95

    # 4. Technical analysis.
    elif contains_phrase(
        text,
        [
            "rsi",
            "macd",
            "bollinger",
            "moving average",
            "sma",
            "ema",
            "atr",
            "vwap",
            "technical analysis",
            "technical indicators",
        ]
    ):
        intent = "technical_analysis"
        confidence = 0.95

    # 5. Benchmark comparison.
    elif benchmark and contains_phrase(
        text,
        [
            "compare",
            "compared to",
            "versus",
            "vs",
            "benchmark",
            "performance against",
            "outperform",
        ]
    ):
        intent = "benchmark_comparison"
        confidence = 0.95

    # 6. Stock-to-stock comparison.
    elif (
        len(tickers) >= 2
        and contains_phrase(
            text,
            ["compare", "versus", "vs", "comparison"]
        )
    ):
        intent = "stock_comparison"
        confidence = 0.95
    
    elif contains_phrase(
        text,
        [
            "health score",
            "portfolio health",
            "health of my portfolio",
            "how healthy is my portfolio",
            "portfolio risk assessment",
            "assess my portfolio",
            "portfolio risk profile",
        ]
    ):
        intent = "portfolio_health"
        confidence = 0.95

    # 7. Diversification and concentration analysis.
    elif contains_phrase(
        text,
        [
            "diversification",
            "diversified",
            "concentration",
            "largest holding",
            "portfolio exposure",
            "sector allocation",
            "sector exposure",
            "asset allocation",
        ]
    ):
        intent = "diversification"
        confidence = 0.95

    # 8. Correlation analysis.
    elif contains_phrase(
        text,
        [
            "correlation",
            "correlated",
            "move together",
        ]
    ):
        intent = "correlation"
        confidence = 0.95

    # 9. Portfolio summary.
    elif (
        contains_phrase(
            text,
            [
                "my portfolio",
                "portfolio summary",
                "portfolio value",
                "how is my portfolio",
                "show my holdings",
                "my holdings",
                "portfolio overview",
            ]
        )
        and not contains_phrase(
            text,
            [
                "performance",
                "performing",
                "returns",
                "volatility",
                "sharpe",
                "beta",
                "drawdown",
                "profit",
                "loss",
            ]
        )
    ):
        intent = "portfolio_summary"
        confidence = 0.90
    # 11. Stock price.
    elif (
        contains_phrase(
            text,
            [
                "stock price",
                "share price",
                "current price",
                "latest price",
                "price of",
                "price for",
                "how much is",
                "how much does",
                "trading price",
                "stock quote",
                "market price",
                "latest stock price",
                "current stock price",
            ]
        )
        or bool(
            re.search(
                r"\b(?:price|quote)\b",
                text
            )
        )
    ):
        intent = "stock_price"
        confidence = 0.95

    # 10. Company information.
    elif (
        not re.search(r"\b(price|quote)\b", text)
        and (
            contains_phrase(
                text,
                [
                    "company information",
                    "tell me about",
                    "what does the company do",
                    "which sector",
                    "company overview",
                    "business model",
                    "give me information about",
                    "give me details about",
                    "information about",
                    "overview of",
                ]
            )
            or bool(
                re.search(
                    r"\bwhat(?:\s+is|'s)\s+(?:the\s+)?"
                    r"[a-z][a-z0-9&.-]*"
                    r"(?:\s+[a-z][a-z0-9&.-]*){0,2}\s*[?!.]?$",
                    text
                )
            )
        )
    ):
        intent = "company_information"
        confidence = 0.95

    # 12. Financial performance and risk metrics.
    elif contains_phrase(
        text,
        [
            "sharpe",
            "sortino",
            "volatility",
            "beta",
            "drawdown",
            "returns",
            "performance",
            "performing",
            "profit",
            "loss",
            "calculate risk",
            "risk metrics",
            "annualized return",
            "annualised return",
        ]
    ):
        intent = "performance_metrics"
        confidence = 0.90

    return IntentResult(
        intent=intent,
        confidence=confidence,
        ticker=ticker,
        tickers=tickers,
        period=period,
        benchmark=benchmark,
        portfolio_id=portfolio_id,
        extraction_source="rules",
    )
