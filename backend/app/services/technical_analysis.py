
import numpy as np
import pandas as pd
import yfinance as yf


def calculate_technical_analysis(ticker: str) -> dict:
    """Calculate technical indicators and generate rule-based interpretations."""

    ticker = ticker.strip().upper()

    if not ticker:
        raise ValueError("A stock ticker is required.")

    # Two years provides enough history for the 200-day SMA
    # and the warm-up period needed by other indicators.
    history = yf.download(
        ticker,
        period="2y",
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
    )

    if history.empty:
        raise ValueError(f"No market data found for {ticker}.")

    # Handle yfinance's possible MultiIndex column format.
    if isinstance(history.columns, pd.MultiIndex):
        history.columns = history.columns.get_level_values(0)

    required = {"Close", "High", "Low"}
    if not required.issubset(history.columns):
        raise ValueError("Market data is missing required OHLC columns.")

    df = history[["Close", "High", "Low"]].copy()
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    df = df[~df.index.duplicated(keep="last")].sort_index()

    if len(df) < 200:
        raise ValueError(
            "At least 200 valid daily observations are required."
        )

    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    # --------------------------------------------------
    # 1. SIMPLE MOVING AVERAGES
    # --------------------------------------------------

    df["SMA_20"] = close.rolling(20).mean()
    df["SMA_50"] = close.rolling(50).mean()
    df["SMA_200"] = close.rolling(200).mean()

    # --------------------------------------------------
    # 2. RSI (14) - WILDER-STYLE SMOOTHING
    # --------------------------------------------------

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / 14, min_periods=14, adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / 14, min_periods=14, adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["RSI_14"] = 100 - (100 / (1 + rs))

    df.loc[
        (avg_loss == 0) & (avg_gain > 0), "RSI_14"
    ] = 100

    df.loc[
        (avg_gain == 0) & (avg_loss == 0), "RSI_14"
    ] = 50

    # --------------------------------------------------
    # 3. MACD
    # --------------------------------------------------

    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()

    df["MACD"] = ema_12 - ema_26

    df["MACD_SIGNAL"] = df["MACD"].ewm(
        span=9, adjust=False
    ).mean()

    df["MACD_HISTOGRAM"] = (
        df["MACD"] - df["MACD_SIGNAL"]
    )

    # --------------------------------------------------
    # 4. BOLLINGER BANDS
    # --------------------------------------------------

    rolling_std = close.rolling(20).std(ddof=0)

    df["BB_MIDDLE"] = df["SMA_20"]
    df["BB_UPPER"] = df["SMA_20"] + 2 * rolling_std
    df["BB_LOWER"] = df["SMA_20"] - 2 * rolling_std

    # --------------------------------------------------
    # 5. AVERAGE TRUE RANGE (14)
    # --------------------------------------------------

    previous_close = close.shift(1)

    true_range = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    df["ATR_14"] = true_range.ewm(
        alpha=1 / 14, min_periods=14, adjust=False
    ).mean()

    latest = df.iloc[-1]

    def number(value):
        if pd.isna(value) or not np.isfinite(float(value)):
            return None
        return round(float(value), 4)

    price = number(latest["Close"])
    sma20 = number(latest["SMA_20"])
    sma50 = number(latest["SMA_50"])
    sma200 = number(latest["SMA_200"])
    rsi = number(latest["RSI_14"])
    macd = number(latest["MACD"])
    signal = number(latest["MACD_SIGNAL"])
    histogram = number(latest["MACD_HISTOGRAM"])
    bb_upper = number(latest["BB_UPPER"])
    bb_middle = number(latest["BB_MIDDLE"])
    bb_lower = number(latest["BB_LOWER"])
    atr = number(latest["ATR_14"])

    if any(
        v is None
        for v in [
            price, sma20, sma50, sma200, rsi, macd,
            signal, histogram, bb_upper, bb_middle,
            bb_lower, atr
        ]
    ):
        raise ValueError(
            "Insufficient valid data to calculate all indicators."
        )

    # --------------------------------------------------
    # 6. RULE-BASED INTERPRETATION
    # --------------------------------------------------

    distance_from_sma200 = (
        (price - sma200) / sma200
    ) * 100

    # Long-term trend
    if price > sma200:
        long_term_trend = "Above 200-day SMA"

        long_term_explanation = (
            f"{ticker} is trading {abs(distance_from_sma200):.2f}% "
            "above its 200-day moving average. This indicates that "
            "the current price is stronger than its long-term average "
            "and suggests a positive long-term trend."
        )

    elif price < sma200:
        long_term_trend = "Below 200-day SMA"

        long_term_explanation = (
            f"{ticker} is trading {abs(distance_from_sma200):.2f}% "
            "below its 200-day moving average. This indicates that "
            "the current price is weaker than its long-term average "
            "and suggests a negative long-term trend."
        )

    else:
        long_term_trend = "At 200-day SMA"

        long_term_explanation = (
            f"{ticker} is trading approximately at its 200-day "
            "moving average, indicating that its current price "
            "is close to its long-term average."
        )

    # Moving average alignment
    if sma20 > sma50 > sma200:
        moving_average_state = "Bullish alignment"

        moving_average_explanation = (
            "The 20-day average is above the 50-day average, "
            "which is above the 200-day average. This indicates "
            "that recent prices are generally stronger than "
            "medium-term and long-term price levels."
        )

    elif sma20 < sma50 < sma200:
        moving_average_state = "Bearish alignment"

        moving_average_explanation = (
            "The 20-day average is below the 50-day average, "
            "which is below the 200-day average. This indicates "
            "that recent prices are generally weaker than "
            "medium-term and long-term price levels."
        )

    else:
        moving_average_state = "Mixed alignment"

        moving_average_explanation = (
            "The moving averages do not follow a consistent "
            "bullish or bearish order. This suggests that the "
            "short-term and long-term trends are not fully aligned."
        )

    # RSI
    if rsi >= 70:
        rsi_state = "Potentially overbought"

        rsi_explanation = (
            f"The RSI is {rsi:.2f}, which is above the commonly "
            "used 70 threshold. This suggests strong recent "
            "buying pressure and that the stock may be overbought. "
            "A price correction is possible, but not guaranteed."
        )

    elif rsi <= 30:
        rsi_state = "Potentially oversold"

        rsi_explanation = (
            f"The RSI is {rsi:.2f}, which is below the commonly "
            "used 30 threshold. This suggests strong recent "
            "selling pressure and that the stock may be oversold. "
            "A recovery is possible, but not guaranteed."
        )

    else:
        rsi_state = "Neutral range"

        rsi_explanation = (
            f"The RSI is {rsi:.2f}, which is between 30 and 70. "
            "This indicates that the stock is not currently "
            "showing extreme overbought or oversold conditions."
        )

    # MACD
    if histogram > 0:
        macd_state = "Positive momentum"

        macd_explanation = (
            f"The MACD ({macd:.4f}) is above its signal line "
            f"({signal:.4f}). The positive histogram of "
            f"{histogram:.4f} indicates stronger upward momentum "
            "relative to the signal line."
        )

    elif histogram < 0:
        macd_state = "Negative momentum"

        macd_explanation = (
            f"The MACD ({macd:.4f}) is below its signal line "
            f"({signal:.4f}). The negative histogram of "
            f"{histogram:.4f} indicates weaker downward momentum "
            "relative to the signal line."
        )

    else:
        macd_state = "Neutral momentum"

        macd_explanation = (
            "The MACD and signal line are approximately equal. "
            "This indicates little difference between the two "
            "momentum measures at the latest observation."
        )

    # Volatility
    atr_percentage = (atr / price) * 100

    if atr_percentage >= 5:
        volatility_state = "High"

        volatility_explanation = (
            f"The ATR is {atr:.2f}, equivalent to "
            f"{atr_percentage:.2f}% of the current price. "
            "This indicates relatively large daily price "
            "movements and higher observed volatility."
        )

    elif atr_percentage >= 2:
        volatility_state = "Moderate"

        volatility_explanation = (
            f"The ATR is {atr:.2f}, equivalent to "
            f"{atr_percentage:.2f}% of the current price. "
            "This indicates moderate daily price fluctuations."
        )

    else:
        volatility_state = "Low"

        volatility_explanation = (
            f"The ATR is {atr:.2f}, equivalent to "
            f"{atr_percentage:.2f}% of the current price. "
            "This indicates relatively smaller daily price "
            "movements during the observed period."
        )

    # Bollinger Bands
    if price >= bb_upper:
        bollinger_state = "Near or above upper band"

        bollinger_explanation = (
            "The stock is trading at or above its upper "
            "Bollinger Band. This means its price is near the "
            "upper end of its recent trading range and may "
            "reflect strong upward price movement."
        )

    elif price <= bb_lower:
        bollinger_state = "Near or below lower band"

        bollinger_explanation = (
            "The stock is trading at or below its lower "
            "Bollinger Band. This means its price is near the "
            "lower end of its recent trading range and may "
            "reflect strong downward price movement."
        )

    else:
        bollinger_state = "Within bands"

        bollinger_explanation = (
            "The stock is trading between its upper and lower "
            "Bollinger Bands, within the range defined by its "
            "recent price average and volatility."
        )

    # Overall interpretation
    bullish_signals = sum([
        price > sma200,
        sma20 > sma50 > sma200,
        histogram > 0,
        30 < rsi < 70 and rsi > 50,
    ])

    bearish_signals = sum([
        price < sma200,
        sma20 < sma50 < sma200,
        histogram < 0,
        30 < rsi < 70 and rsi < 50,
    ])

    if bullish_signals >= 3:
        overall_summary = (
            f"The technical indicators for {ticker} show a "
            "generally positive pattern. The majority of the "
            "measured trend and momentum signals are positive. "
            "However, these indicators describe historical price "
            "behaviour and do not guarantee future performance."
        )

    elif bearish_signals >= 3:
        overall_summary = (
            f"The technical indicators for {ticker} show a "
            "generally negative pattern. The majority of the "
            "measured trend and momentum signals are negative. "
            "However, these indicators describe historical price "
            "behaviour and do not guarantee future performance."
        )

    else:
        overall_summary = (
            f"The technical indicators for {ticker} show a mixed "
            "pattern. Some signals may indicate positive movement "
            "while others suggest weaker or neutral conditions. "
            "There is no clear overall direction across the "
            "measured indicators."
        )

    latest_date = df.index[-1].strftime("%Y-%m-%d")

    # --------------------------------------------------
    # 7. CHART DATA
    # --------------------------------------------------

    chart_columns = [
        "Close", "SMA_20", "SMA_50", "SMA_200",
        "RSI_14", "MACD", "MACD_SIGNAL",
        "MACD_HISTOGRAM", "BB_UPPER", "BB_MIDDLE",
        "BB_LOWER", "ATR_14",
    ]

    chart = []

    for date, row in df.tail(260)[chart_columns].iterrows():
        chart.append({
            "date": date.strftime("%Y-%m-%d"),
            **{
                column.lower(): number(row[column])
                for column in chart_columns
            },
        })

    # --------------------------------------------------
    # 8. RESPONSE
    # --------------------------------------------------

    return {
        "ticker": ticker,
        "data_source": "Yahoo Finance via yfinance",
        "data_date": latest_date,
        "current_price": price,

        "indicators": {
            "sma_20": sma20,
            "sma_50": sma50,
            "sma_200": sma200,
            "distance_from_sma200_pct": round(
                float(distance_from_sma200), 2
            ),
            "rsi_14": rsi,
            "macd": macd,
            "macd_signal": signal,
            "macd_histogram": histogram,
            "bollinger_upper": bb_upper,
            "bollinger_middle": bb_middle,
            "bollinger_lower": bb_lower,
            "atr_14": atr,
            "atr_pct_of_price": round(
                float(atr_percentage), 2
            ),
        },

        "interpretation": {
            # EXISTING FIELDS - PRESERVED FOR CHATBOT
            "long_term_trend": long_term_trend,
            "moving_average_alignment": moving_average_state,
            "rsi": rsi_state,
            "macd": macd_state,
            "volatility": volatility_state,

            # NEW PLAIN-LANGUAGE INTERPRETATIONS
            "long_term_trend_explanation": long_term_explanation,
            "moving_average_explanation": moving_average_explanation,
            "rsi_explanation": rsi_explanation,
            "macd_explanation": macd_explanation,
            "volatility_explanation": volatility_explanation,
            "bollinger_state": bollinger_state,
            "bollinger_explanation": bollinger_explanation,

            # EXISTING FIELD - PRESERVED FOR CHATBOT
            "explanation": (
                f"{ticker} closed at {price} on {latest_date}, "
                f"{distance_from_sma200:.2f}% relative to its "
                f"200-day SMA. RSI is {rsi:.2f} "
                f"({rsi_state.lower()}), and the MACD histogram "
                f"is {histogram:.4f} ({macd_state.lower()}). "
                "These indicators describe historical price "
                "behaviour and do not predict future returns."
            ),

            # NEW COMBINED INTERPRETATION
            "overall_summary": overall_summary,
        },

        "chart": chart,

        "disclaimer": (
            "For educational analysis only; not financial advice."
        ),
    }
