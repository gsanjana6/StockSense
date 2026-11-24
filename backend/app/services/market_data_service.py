
from datetime import date, datetime, timedelta
import logging

import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session

from app.models.price_cache import PriceCache

logger = logging.getLogger(__name__)

PERIOD_DAYS = {
    "1mo": 31,
    "3mo": 93,
    "6mo": 186,
    "1y": 366,
    "2y": 732,
    "5y": 1830,
    "10y": 3660,
    "ytd": None,
    "max": None,
}

# Allow weekends and ordinary market holidays.
MAX_CACHE_AGE_DAYS = 7


def _normalize_ticker(ticker: str) -> str:
    ticker = ticker.strip().upper()
    if not ticker:
        raise ValueError("A stock ticker is required.")
    return ticker


def _fetch_yahoo_history(ticker: str, period: str) -> pd.DataFrame | None:
    try:
        data = yf.Ticker(ticker).history(
            period=period,
            auto_adjust=False
        )

        if data is None or data.empty:
            return None

        data = data.copy()
        data = data.dropna(subset=["Close"])

        if data.empty:
            return None

        return data

    except Exception:
        logger.exception("Yahoo Finance history request failed for %s", ticker)
        return None


def _cache_to_dataframe(rows: list[PriceCache]) -> pd.DataFrame | None:
    if not rows:
        return None

    records = []

    for row in rows:
        records.append({
            "Open": float(row.open) if row.open is not None else None,
            "High": float(row.high) if row.high is not None else None,
            "Low": float(row.low) if row.low is not None else None,
            "Close": float(row.close) if row.close is not None else None,
            "Volume": int(row.volume) if row.volume is not None else 0,
        })

    df = pd.DataFrame(
        records,
        index=pd.to_datetime([row.price_date for row in rows])
    )

    df.index.name = "Date"
    return df.sort_index()


def get_current_price(ticker: str, db: Session = None):
    """
    Return the latest available closing price.

    Uses the database first. Yahoo Finance is queried only when the
    cached price is missing or older than MAX_CACHE_AGE_DAYS.
    """
    ticker = _normalize_ticker(ticker)

    cached_price = None

    if db is not None:
        try:
            cached_price = (
                db.query(PriceCache)
                .filter(
                    PriceCache.ticker == ticker,
                    PriceCache.close.isnot(None)
                )
                .order_by(PriceCache.price_date.desc())
                .first()
            )

            if cached_price is not None:
                cache_age = (date.today() - cached_price.price_date).days

                if cache_age <= MAX_CACHE_AGE_DAYS:
                    return float(cached_price.close)

        except Exception:
            logger.exception("Price cache lookup failed for %s", ticker)

    # Cache is missing or stale. Fetch a small recent window.
    data = _fetch_yahoo_history(ticker, "5d")

    if data is not None and not data.empty:
        latest_row = data.iloc[-1]
        latest_price = float(latest_row["Close"])

        # Save the latest daily record to avoid repeating the request.
        if db is not None:
            try:
                latest_date = data.index[-1].date()

                existing = (
                    db.query(PriceCache)
                    .filter(
                        PriceCache.ticker == ticker,
                        PriceCache.price_date == latest_date
                    )
                    .first()
                )

                if existing is None:
                    db.add(PriceCache(
                        ticker=ticker,
                        price_date=latest_date,
                        open=float(latest_row["Open"]),
                        high=float(latest_row["High"]),
                        low=float(latest_row["Low"]),
                        close=latest_price,
                        volume=int(latest_row["Volume"])
                    ))
                else:
                    existing.close = latest_price

                db.commit()

            except Exception:
                db.rollback()
                logger.exception("Could not cache latest price for %s", ticker)

        return latest_price

    # If Yahoo is unavailable, use the last cached close even if stale.
    if cached_price is not None:
        logger.warning("Using stale cached price for %s", ticker)
        return float(cached_price.close)

    logger.warning("No price available for %s", ticker)
    return None


def get_historical_prices(
    ticker: str,
    period: str = "1y",
    db: Session = None
):
    """
    Return historical OHLCV data.

    If a database session is supplied, cached records are checked first.
    Yahoo Finance is used when no cached history is available or the
    latest cached record is too old.
    """
    ticker = _normalize_ticker(ticker)

    if period not in PERIOD_DAYS:
        raise ValueError(f"Unsupported historical period: {period}")

    cached_df = None

    if db is not None:
        try:
            query = db.query(PriceCache).filter(
                PriceCache.ticker == ticker,
                PriceCache.close.isnot(None)
            )

            days = PERIOD_DAYS[period]

            if days is not None:
                start_date = date.today() - timedelta(days=days)
                query = query.filter(PriceCache.price_date >= start_date)

            rows = query.order_by(PriceCache.price_date.asc()).all()
            cached_df = _cache_to_dataframe(rows)

            if cached_df is not None and not cached_df.empty:
                latest_cached_date = cached_df.index[-1].date()
                cache_age = (date.today() - latest_cached_date).days

                if cache_age <= MAX_CACHE_AGE_DAYS:
                    return cached_df

        except Exception:
            logger.exception("Historical cache lookup failed for %s", ticker)

    # No usable cache: fetch from Yahoo Finance.
    fresh_df = _fetch_yahoo_history(ticker, period)

    if fresh_df is not None and not fresh_df.empty:
        if db is not None:
            cache_historical_prices(
                ticker=ticker,
                db=db,
                period=period,
                source_data=fresh_df
            )

        return fresh_df

    # Yahoo failed: return whatever cache is available.
    return cached_df


def cache_historical_prices(
    ticker: str,
    db: Session,
    period: str = "1y",
    source_data: pd.DataFrame = None
):
    """
    Cache historical OHLCV records.

    Existing dates are loaded in one query, avoiding one SELECT per row.
    """
    ticker = _normalize_ticker(ticker)

    data = source_data

    if data is None:
        data = _fetch_yahoo_history(ticker, period)

    if data is None or data.empty:
        return 0

    try:
        incoming_dates = [timestamp.date() for timestamp in data.index]

        existing_dates = set(
            row[0]
            for row in db.query(PriceCache.price_date)
            .filter(
                PriceCache.ticker == ticker,
                PriceCache.price_date.in_(incoming_dates)
            )
            .all()
        )

        new_records = []

        for timestamp, row in data.iterrows():
            price_date = timestamp.date()

            if price_date in existing_dates:
                continue

            required_values = [
                row.get("Open"),
                row.get("High"),
                row.get("Low"),
                row.get("Close")
            ]

            if any(pd.isna(value) for value in required_values):
                continue

            volume = row.get("Volume", 0)

            new_records.append(PriceCache(
                ticker=ticker,
                price_date=price_date,
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=int(volume) if pd.notna(volume) else 0
            ))

        if new_records:
            db.add_all(new_records)
            db.commit()

        return len(new_records)

    except Exception:
        db.rollback()
        logger.exception("Failed to cache historical prices for %s", ticker)
        return 0
