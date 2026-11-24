
import re
import logging
from typing import Any

logger = logging.getLogger(__name__)


NUMBER_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])[-+]?\$?\s*\d[\d,]*(?:\.\d+)?\s*%?"
)

TICKER_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])\$?([A-Z]{2,5})(?![A-Za-z0-9])"
)

NON_TICKER_TERMS = {
    "USD", "RSI", "MACD", "SMA", "EMA", "ATR",
    "ETF", "IPO", "EPS", "PE", "GDP", "ROI",
    "AI", "API", "LLM", "THE", "AND", "FOR",
    "WITH", "FROM", "THIS", "THAT", "YOUR",
    "OVER", "PER", "NOT", "ARE", "BUT", "VS",
    "CEO", "CAGR", "ROE", "ROA", "DCF"
}


# Longer aliases are checked first to avoid matching a generic
# word before a more specific metric label.
METRIC_ALIASES = {
    "price": (
        "closing price", "latest close", "current price",
        "market price", "stock price", "price"
    ),
    "return": (
        "annualised return", "annualized return",
        "historical return", "total return",
        "portfolio return", "returns", "return"
    ),
    "difference": (
        "percentage-point difference",
        "percentage points",
        "difference",
        "outperformance",
        "underperformance"
    ),
    "volatility": (
        "annualised volatility", "annualized volatility",
        "volatility"
    ),
    "sharpe": ("sharpe ratio", "sharpe"),
    "drawdown": (
        "maximum drawdown", "max drawdown", "drawdown"
    ),
    "beta": ("portfolio beta", "beta"),
    "market_cap": (
        "market capitalisation", "market capitalization",
        "market cap"
    ),
    "concentration": (
        "concentration index", "concentration"
    ),
    "holdings": (
        "effective holdings", "holdings", "holding"
    ),
    "weight": (
        "portfolio weight", "largest weight",
        "allocation", "weight"
    ),
    "observations": ("observations", "data points"),
    "recovery": (
        "recovery days", "recovery period",
        "trading days to recover"
    ),
    "rsi": ("rsi",),
    "sma": ("moving average", "sma"),
    "macd": ("macd",),
    "atr": ("atr",),
    "correlation": ("correlation",),
    "health_score": (
        "health score",
        "portfolio health score"
    ),
}


SOURCE_KEY_ALIASES = {
    "price": ("price", "close"),
    "return": ("return", "performance"),
    "difference": (
        "difference_percentage_points",
        "difference"
    ),
    "volatility": ("volatility",),
    "sharpe": ("sharpe",),
    "drawdown": ("drawdown",),
    "beta": ("beta",),
    "market_cap": ("market_cap", "market cap"),
    "concentration": ("concentration",),
    "holdings": ("holdings", "effective_holdings"),
    "weight": ("weight", "allocation"),
    "observations": ("observations",),
    "recovery": ("recovery_days", "recovery_period"),
    "rsi": ("rsi",),
    "sma": ("sma", "moving_average"),
    "macd": ("macd",),
    "atr": ("atr",),
    "correlation": ("correlation",),
    "health_score": ("health_score",)
}


def _collect_source_data(
    data: Any,
    path: str = ""
) -> tuple[list[tuple[str, float]], set[str]]:

    numeric_values = []
    tickers = set()

    if isinstance(data, dict):
        for key, value in data.items():
            key_text = str(key).lower()
            child_path = f"{path} {key_text}".strip()

            if key_text in {"ticker", "benchmark", "benchmark_ticker"}:
                if isinstance(value, str):
                    tickers.add(value.upper())
                        # Collect ticker symbols used as correlation matrix keys.
            
            elif path.endswith("correlation matrix") and isinstance(value, dict):
                tickers.add(str(key).upper())

            elif key_text == "tickers":
                if isinstance(value, str):
                    tickers.add(value.upper())
                elif isinstance(value, (list, tuple, set)):
                    tickers.update(
                        str(item).upper()
                        for item in value
                        if isinstance(item, str)
                    )

            child_numbers, child_tickers = _collect_source_data(
                value, child_path
            )

            numeric_values.extend(child_numbers)
            tickers.update(child_tickers)

    elif isinstance(data, (list, tuple)):
        for item in data:
            child_numbers, child_tickers = _collect_source_data(
                item, path
            )

            numeric_values.extend(child_numbers)
            tickers.update(child_tickers)

    elif isinstance(data, (int, float)) and not isinstance(data, bool):
        numeric_values.append((path, float(data)))

    return numeric_values, tickers


def _normalise_number(value: str) -> float:
    cleaned = (
        value.replace("$", "")
        .replace(",", "")
        .replace("%", "")
        .strip()
    )
    return float(cleaned)


def _metric_matches_source_key(
    metric: str,
    source_key: str
) -> bool:

    key = source_key.lower()

    return any(
        alias in key
        for alias in SOURCE_KEY_ALIASES.get(metric, ())
    )


def _find_metric_mentions(
    text: str
) -> list[tuple[int, int, str]]:

    mentions = []

    for metric, aliases in METRIC_ALIASES.items():
        for alias in sorted(aliases, key=len, reverse=True):
            pattern = re.compile(
                rf"(?<![a-zA-Z0-9_]){re.escape(alias)}"
                rf"(?![a-zA-Z0-9_])",
                re.IGNORECASE
            )

            for match in pattern.finditer(text):
                mentions.append(
                    (match.start(), match.end(), metric)
                )

    # Remove overlapping aliases, preferring the longest match.
    mentions.sort(
        key=lambda item: (
            item[0],
            -(item[1] - item[0])
        )
    )

    filtered = []

    for mention in mentions:
        start, end, metric = mention

        overlaps = any(
            start < existing_end and end > existing_start
            for existing_start, existing_end, _ in filtered
        )

        if not overlaps:
            filtered.append(mention)

    return sorted(filtered, key=lambda item: item[0])


def _get_sentence(
    text: str,
    position: int
) -> tuple[str, int, int]:

    boundaries = list(
        re.finditer(r"[.!?](?:\s+|$)|\n+", text)
    )

    start = 0
    end = len(text)

    for boundary in boundaries:
        if boundary.end() <= position:
            start = boundary.end()
        elif boundary.start() > position:
            end = boundary.start()
            break

    return text[start:end], start, end


def _find_metric_for_number(
    response: str,
    number_position: int,
    mentions: list[tuple[int, int, str]]
) -> str | None:

    sentence, sentence_start, sentence_end = _get_sentence(
        response, number_position
    )

    sentence_lower = sentence.lower()

    # Infer return from explicit portfolio growth language.
    if re.search(
        r"\b(portfolio|investment|investments)\b.{0,50}"
        r"\b(grew|growth|increased|earned|gained|generated)\b",
        sentence_lower
    ):
        return "return"
    # Infer portfolio weight from largest-holding language.
    if re.search(
        r"\b(largest|biggest|top)\s+holding\b"
        r"|\bholding\s+accounts\s+for\b"
        r"|\bportfolio\s+allocation\b",
        sentence_lower
    ):
        return "weight"
    # Infer drawdown from explicit peak-to-trough decline language.
    if re.search(
        r"\b(drawdown|peak[- ]to[- ]trough|from a peak)\b",
        sentence_lower
    ):
        return "drawdown"
    
    # Infer benchmark difference from comparative language.
    if re.search(
        r"\b(outperformed|outperformance|underperformed|"
        r"exceeded|outpaced|surpassed)\b",
        sentence_lower
    ) and re.search(
        r"\b(by|difference|more than|less than)\b",
        sentence_lower
    ):
        return "difference"
    local_mentions = [
        mention
        for mention in mentions
        if sentence_start <= mention[0] < sentence_end
    ]

    if local_mentions:
        nearest = min(
            local_mentions,
            key=lambda item: abs(
                number_position - (item[0] + item[1]) / 2
            )
        )
        return nearest[2]

    return None


def _is_contextual_number(
    response: str,
    start: int,
    end: int
) -> bool:

    raw = response[start:end].strip()
    clean_number = raw.rstrip(",;:")

    # Ignore numbers appearing inside ISO dates such as 2026-11-23.
    for date_match in re.finditer(
        r"\b\d{4}-\d{2}-\d{2}\b",
        response
    ):
        if date_match.start() <= start < date_match.end():
            return True

    # Ignore dates such as November 23, 2026.
    months = (
        "january|february|march|april|may|june|"
        "july|august|september|october|november|december"
    )

    date_pattern = re.compile(
        rf"\b(?:{months})\s+\d{{1,2}},?\s+\d{{4}}\b",
        re.IGNORECASE
    )

    for date_match in date_pattern.finditer(response):
        if date_match.start() <= start < date_match.end():
            return True

    # Ignore standalone years.
    if re.fullmatch(r"\d{4}", clean_number):
        return True

    # Ignore durations such as 14-day RSI.
    surrounding = response[
        max(0, start - 65):
        min(len(response), end + 65)
    ].lower()
    # Ignore standard correlation-scale reference values
    # when explaining correlation concepts, not reporting
    # an actual measured correlation.
    if "correlation" in surrounding:

        if clean_number in {"1.0", "+1.0", "-1.0"} and re.search(
            r"perfect\s+(positive|negative)",
            surrounding,
            re.IGNORECASE
        ):
            return True

        if clean_number in {"0", "0.0"} and re.search(
            r"no\s+correlation",
            surrounding,
            re.IGNORECASE
        ):
            return True
    # Ignore standard technical indicator periods:
    # SMA 20, SMA 50, SMA 200 and RSI 14.
    preceding_text = response[max(0, start - 40):start]

    if re.search(
        r"\b(?:SMA|RSI)\s*$",
        preceding_text,
        re.IGNORECASE
    ):
        return True

    # Ignore RSI scale boundaries in descriptions such as
    # "scale of 0 to 100" or "0 to 100, with".
    if clean_number in {"0", "100"} and re.search(
        r"\bscale\s+of\s+0\s+to\s+100\b",
        surrounding,
        re.IGNORECASE
    ):
        return True
    # --- ADDED HERE ---
    # Ignore 500 when referring to the S&P 500 index
    # or its 500 constituent companies.
    if clean_number == "500" and re.search(
        r"\bS\s*&\s*P\s*500\b|\b500\s+largest\b",
        surrounding,
        re.IGNORECASE
    ):
        return True
    
    if re.search(
        rf"\b{re.escape(clean_number)}\s*[- ]?"
        r"(?:year|years|day|days|month|months)\b",
        surrounding
    ):
        return True

    # Ignore the endpoints of the standard 0-to-100 RSI scale.
    if clean_number in {"0", "100"}:
        scale_pattern = re.compile(
            r"\b0\s*(?:to|-)\s*100\s+scale\b",
            re.IGNORECASE
        )

        for scale_match in scale_pattern.finditer(response):
            if scale_match.start() <= start < scale_match.end():
                return True

    # Ignore 70 as the standard overbought threshold.
    if clean_number == "70" and re.search(
        r"\boverbought\b.{0,80}\babove\s+70\b"
        r"|\babove\s+70\b.{0,80}\boverbought\b",
        surrounding
    ):
        return True

    # Ignore 30 as the standard oversold threshold.
    if clean_number == "30" and re.search(
        r"\boversold\b.{0,80}\bbelow\s+30\b"
        r"|\bbelow\s+30\b.{0,80}\boversold\b",
        surrounding
    ):
        return True

    # Ignore general Sharpe ratio benchmarks.
    if re.search(
        r"(?:above|below|greater than|less than|exceed)"
        r"\s+" + re.escape(clean_number),
        surrounding
    ) and "sharpe" in surrounding:
        return True
    # Ignore the maximum score in a health score expressed out of 100.
    if clean_number == "100" and re.search(
        r"\bhealth score\b.{0,30}\bout of 100\b",
        surrounding,
        re.IGNORECASE
    ):
        return True
    
    return False

def _is_supported(
    claimed_value: float,
    source_value: float,
    metric: str,
    surrounding_text: str
) -> bool:

    tolerance = max(
        0.02,
        abs(source_value) * 0.001
    )

    # Exact value or ordinary decimal rounding.
    if abs(claimed_value - source_value) <= tolerance:
        return True

    # Drawdown can be reported as a positive magnitude.
    if (
        metric == "drawdown"
        and abs(abs(claimed_value) - abs(source_value)) <= tolerance
    ):
        return True

    # Allow whole-number rounding for percentage metrics.
    if (
        "%" in surrounding_text
        and round(claimed_value) == round(source_value)
    ):
        return True

    # Allow explicitly approximate descriptions.
    approximate_words = (
        "nearly", "approximately", "about",
        "around", "roughly", "almost"
    )

    has_approximation = any(
        word in surrounding_text.lower()
        for word in approximate_words
    )

    if has_approximation:
        if abs(claimed_value - source_value) <= 0.5:
            return True

        if (
            metric == "drawdown"
            and abs(abs(claimed_value) - abs(source_value)) <= 0.5
        ):
            return True

    return False


def verify_llm_response(
    response: str,
    context: dict
) -> dict:

    if not isinstance(response, str) or not response.strip():
        return {
            "status": "failed",
            "reason": "Missing generated response."
        }

    if not isinstance(context, dict) or not context:
        return {
            "status": "failed",
            "reason": "Missing structured source data."
        }

    source_numbers, source_tickers = _collect_source_data(context)

    mentioned_tickers = {
        ticker
        for ticker in TICKER_PATTERN.findall(response)
        if ticker not in NON_TICKER_TERMS
    }

    unsupported_tickers = mentioned_tickers - source_tickers

    unsupported_numbers = []
    unverifiable_numbers = []

    metric_mentions = _find_metric_mentions(response)

    for match in NUMBER_PATTERN.finditer(response):
        raw_number = match.group().strip()

        if _is_contextual_number(
            response,
            match.start(),
            match.end()
        ):
            continue

        try:
            value = _normalise_number(raw_number)
        except ValueError:
            continue

        # Ignore standalone year references.
        if re.fullmatch(r"\d{4}", raw_number):
            continue

        metric = _find_metric_for_number(
            response,
            match.start(),
            metric_mentions
        )

        if metric is None:
            unverifiable_numbers.append(raw_number)
            continue

        relevant_values = [
            source_value
            for source_key, source_value in source_numbers
            if _metric_matches_source_key(metric, source_key)
        ]

        if not relevant_values:
            unverifiable_numbers.append(raw_number)
            continue

        surrounding_text = response[
            max(0, match.start() - 50):
            min(len(response), match.end() + 50)
        ]

        supported = any(
            _is_supported(
                value,
                source_value,
                metric,
                surrounding_text
            )
            for source_value in relevant_values
        )

        if not supported:
            unsupported_numbers.append(raw_number)

    failed = (
        bool(unsupported_tickers)
        or bool(unsupported_numbers)
        or bool(unverifiable_numbers)
    )

    result = {
        "status": "failed" if failed else "passed",
        "reason": (
            "Some claims could not be verified against their "
            "corresponding structured data fields."
            if failed else None
        ),
        "unsupported_tickers": sorted(unsupported_tickers),
        "unsupported_numbers": unsupported_numbers,
        "unverifiable_numbers": unverifiable_numbers
    }

    logger.info("LLM response verification result: %s", result)

    return result
