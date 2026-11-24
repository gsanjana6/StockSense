
from datetime import date

from sqlalchemy.orm import Session

from app.services.snapshot_service import get_portfolio_snapshot_history
from app.services.market_data_service import get_historical_prices


def get_portfolio_benchmark_history(
    portfolio_id: int,
    db: Session,
    benchmark_ticker: str = "SPY"
):
    snapshots = get_portfolio_snapshot_history(
        portfolio_id,
        db
    )

    snapshots = [
        snapshot
        for snapshot in snapshots
        if snapshot.get("total_value") is not None
    ]

    if len(snapshots) < 2:
        return []

    benchmark_data = get_historical_prices(
        ticker=benchmark_ticker,
        period="1y",
        db=db
    )

    if benchmark_data is None or benchmark_data.empty:
        return []

    benchmark_data = benchmark_data.dropna(subset=["Close"])

    if benchmark_data.empty:
        return []

    benchmark_data.index = benchmark_data.index.date

    # A dictionary avoids repeatedly scanning the DataFrame.
    benchmark_prices = {
        trading_date: float(row["Close"])
        for trading_date, (_, row) in zip(
            benchmark_data.index,
            benchmark_data.iterrows()
        )
    }

    benchmark_dates = sorted(benchmark_prices)

    history = []

    for snapshot in snapshots:
        snapshot_date = date.fromisoformat(snapshot["date"])

        eligible_dates = [
            trading_date
            for trading_date in benchmark_dates
            if trading_date <= snapshot_date
        ]

        if not eligible_dates:
            continue

        nearest_date = eligible_dates[-1]

        history.append({
            "date": snapshot["date"],
            "portfolio": float(snapshot["total_value"]),
            "benchmark": benchmark_prices[nearest_date]
        })

    return history
