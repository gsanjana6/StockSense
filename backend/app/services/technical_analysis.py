
import numpy as np
import pandas as pd
import yfinance as yf


def calculate_technical_analysis(ticker: str) -> dict:
    """Calculate technical indicators for a supported stock or ETF."""

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

    # Simple moving averages
    df["SMA_20"] = close.rolling(20).mean()
    df["SMA_50"] = close.rolling(50).mean()
    df["SMA_200"] = close.rolling(200).mean()

    # RSI (14), using Wilder-style exponential smoothing
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

    # Handle a run of gains with no losses.
    df.loc[(avg_loss == 0) & (avg_gain > 0), "RSI_14"] = 100
    df.loc[(avg_gain == 0) & (avg_loss == 0), "RSI_14"] = 50

    # MACD: EMA(12) - EMA(26), with EMA(9) signal
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()

    df["MACD"] = ema_12 - ema_26
    df["MACD_SIGNAL"] = df["MACD"].ewm(
        span=9, adjust=False
    ).mean()
    df["MACD_HISTOGRAM"] = (
        df["MACD"] - df["MACD_SIGNAL"]
    )

    # Bollinger Bands: SMA(20) +/- 2 standard deviations
    rolling_std = close.rolling(20).std(ddof=0)
    df["BB_MIDDLE"] = df["SMA_20"]
    df["BB_UPPER"] = df["SMA_20"] + 2 * rolling_std
    df["BB_LOWER"] = df["SMA_20"] - 2 * rolling_std

    # Average True Range (14)
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

    if any(v is None for v in [price, sma20, sma50, sma200,
                                rsi, macd, signal, histogram,
                                bb_upper, bb_middle, bb_lower, atr]):
        raise ValueError(
            "Insufficient valid data to calculate all indicators."
        )

    distance_from_sma200 = ((price - sma200) / sma200) * 100

    if price > sma200:
        long_term_trend = "Above 200-day SMA"
    elif price < sma200:
        long_term_trend = "Below 200-day SMA"
    else:
        long_term_trend = "At 200-day SMA"

    if rsi >= 70:
        rsi_state = "Potentially overbought"
    elif rsi <= 30:
        rsi_state = "Potentially oversold"
    else:
        rsi_state = "Neutral range"

    if histogram > 0:
        macd_state = "Positive momentum"
    elif histogram < 0:
        macd_state = "Negative momentum"
    else:
        macd_state = "Neutral momentum"

    atr_percentage = (atr / price) * 100

    if atr_percentage >= 5:
        volatility_state = "High"
    elif atr_percentage >= 2:
        volatility_state = "Moderate"
    else:
        volatility_state = "Low"

    if sma20 > sma50 > sma200:
        moving_average_state = "Bullish alignment"
    elif sma20 < sma50 < sma200:
        moving_average_state = "Bearish alignment"
    else:
        moving_average_state = "Mixed alignment"

    latest_date = df.index[-1].strftime("%Y-%m-%d")

    # Return recent observations for frontend charting.
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
            "atr_pct_of_price": round(float(atr_percentage), 2),
        },
        "interpretation": {
            "long_term_trend": long_term_trend,
            "moving_average_alignment": moving_average_state,
            "rsi": rsi_state,
            "macd": macd_state,
            "volatility": volatility_state,
            "explanation": (
                f"{ticker} closed at {price} on {latest_date}, "
                f"{distance_from_sma200:.2f}% relative to its "
                "200-day SMA. RSI is "
                f"{rsi:.2f} ({rsi_state.lower()}), and the MACD "
                f"histogram is {histogram:.4f} ({macd_state.lower()}). "
                "These indicators describe historical price behaviour "
                "and do not predict future returns."
            ),
        },
        "chart": chart,
        "disclaimer": (
            "For educational analysis only; not financial advice."
        ),
    }
