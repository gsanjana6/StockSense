import yfinance as yf

from sqlalchemy.orm import Session

from app.models.price_cache import PriceCache


def get_current_price(
    ticker: str,
    db: Session = None
):
    ticker = ticker.upper().strip()

    # ---------------------------------------------------------
    # 1. Try live price from Yahoo Finance
    # ---------------------------------------------------------
    try:
        stock = yf.Ticker(ticker)

        data = stock.history(
            period="5d",
            auto_adjust=False
        )

        if data is not None and not data.empty:
            data = data.dropna(subset=["Close"])

            if not data.empty:
                current_price = data["Close"].iloc[-1]

                return float(current_price)

    except Exception as e:
        print(
            f"Live market data error for {ticker}: {e}"
        )

    # ---------------------------------------------------------
    # 2. Try cached price from database
    # ---------------------------------------------------------
    if db is not None:
        try:
            cached_price = (
                db.query(PriceCache)
                .filter(
                    PriceCache.ticker == ticker,
                    PriceCache.close.isnot(None)
                )
                .order_by(
                    PriceCache.price_date.desc()
                )
                .first()
            )

            if cached_price is not None:
                print(
                    f"Using cached price for {ticker}: "
                    f"{cached_price.close}"
                )

                return float(cached_price.close)

        except Exception as e:
            print(
                f"Price cache lookup failed for "
                f"{ticker}: {e}"
            )

    # ---------------------------------------------------------
    # 3. Nothing available
    # ---------------------------------------------------------
    print(
        f"No current or cached price available "
        f"for {ticker}"
    )

    return None


def get_historical_prices(
    ticker: str,
    period: str = "1y"
):
    ticker = ticker.upper().strip()

    try:
        stock = yf.Ticker(ticker)

        data = stock.history(
            period=period,
            auto_adjust=False
        )

        if data is None or data.empty:
            return None

        return data

    except Exception as e:
        print(
            f"Historical market data error "
            f"for {ticker}: {e}"
        )

        return None


def cache_historical_prices(
    ticker: str,
    db: Session,
    period: str = "1y"
):
    ticker = ticker.upper().strip()

    data = get_historical_prices(
        ticker,
        period
    )

    if data is None or data.empty:
        return 0

    rows_added = 0

    for date, row in data.iterrows():

        price_date = date.date()

        existing_price = (
            db.query(PriceCache)
            .filter(
                PriceCache.ticker == ticker,
                PriceCache.price_date == price_date
            )
            .first()
        )

        if existing_price:
            continue

        if (
            row["Open"] is None
            or row["High"] is None
            or row["Low"] is None
            or row["Close"] is None
        ):
            continue

        new_price = PriceCache(
            ticker=ticker,
            price_date=price_date,
            open=float(row["Open"]),
            high=float(row["High"]),
            low=float(row["Low"]),
            close=float(row["Close"]),
            volume=int(row["Volume"])
        )

        db.add(new_price)
        rows_added += 1

    try:
        db.commit()

        return rows_added

    except Exception as e:
        db.rollback()

        print(
            f"Failed to cache historical prices "
            f"for {ticker}: {e}"
        )

        return 0