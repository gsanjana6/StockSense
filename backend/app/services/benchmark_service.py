from datetime import date

from sqlalchemy.orm import Session

from app.services.snapshot_service import get_portfolio_snapshot_history
from app.services.market_data_service import get_historical_prices


def get_portfolio_benchmark_history(
    portfolio_id: int,
    db: Session,
    benchmark_ticker: str = "SPY"
):
    # ---------------------------------------------------------
    # 1. Load this portfolio's daily value snapshots
    # ---------------------------------------------------------

    snapshots = get_portfolio_snapshot_history(
        portfolio_id,
        db
    )

    snapshots = [
        s for s in snapshots
        if s.get("total_value") is not None
    ]

    if len(snapshots) < 2:
        # Not enough history yet to plot a comparison.
        # Snapshots accumulate daily via the scheduler / POST /snapshots.
        return []

    # ---------------------------------------------------------
    # 2. Load up to a year of benchmark (SPY) closing prices
    # ---------------------------------------------------------

    benchmark_data = get_historical_prices(
        benchmark_ticker,
        period="1y"
    )

    if benchmark_data is None or benchmark_data.empty:
        return []

    benchmark_data = benchmark_data.dropna(subset=["Close"])

    benchmark_dates = sorted(
        d.date() for d in benchmark_data.index.to_pydatetime()
    )

    def closest_close(target_date: date):
        # Find the latest benchmark trading day on or before target_date,
        # so weekends/holidays in portfolio snapshots still resolve to
        # the most recent available SPY close.
        candidates = [d for d in benchmark_dates if d <= target_date]

        if not candidates:
            return None

        nearest = max(candidates)

        row = benchmark_data.loc[
            benchmark_data.index.date == nearest
        ]

        if row.empty:
            return None

        return float(row["Close"].iloc[0])

    # ---------------------------------------------------------
    # 3. Build an aligned {date, portfolio, benchmark} series
    # ---------------------------------------------------------

    history = []

    for snapshot in snapshots:
        snapshot_date = date.fromisoformat(snapshot["date"])
        benchmark_close = closest_close(snapshot_date)

        if benchmark_close is None:
            continue

        history.append({
            "date": snapshot["date"],
            "portfolio": float(snapshot["total_value"]),
            "benchmark": benchmark_close,
        })

    return history
