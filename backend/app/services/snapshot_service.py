from datetime import date
from sqlalchemy.orm import Session

from app.models.portfolio_snapshot import PortfolioSnapshot
from app.services.portfolio_service import calculate_portfolio_value
from app.services.analytics_service import get_portfolio_returns

def get_portfolio_snapshot_history(
    portfolio_id: int,
    db: Session
):
    snapshots = (
        db.query(PortfolioSnapshot)
        .filter(
            PortfolioSnapshot.portfolio_id == portfolio_id
        )
        .order_by(
            PortfolioSnapshot.snapshot_date.asc()
        )
        .all()
    )

    return [
        {
            "snapshot_id": snapshot.snapshot_id,
            "date": snapshot.snapshot_date.isoformat(),
            "total_value": (
                float(snapshot.total_value)
                if snapshot.total_value is not None
                else None
            ),
            "daily_return": (
                float(snapshot.daily_return)
                if snapshot.daily_return is not None
                else None
            )
        }
        for snapshot in snapshots
    ]

def create_portfolio_snapshot(
    portfolio_id: int,
    db: Session
):
    today = date.today()

    # --------------------------------
    # 1. Check for today's snapshot
    # --------------------------------

    existing_snapshot = db.query(
        PortfolioSnapshot
    ).filter(
        PortfolioSnapshot.portfolio_id == portfolio_id,
        PortfolioSnapshot.snapshot_date == today
    ).first()

    # --------------------------------
    # 2. Get current portfolio value
    # --------------------------------

    valuation = calculate_portfolio_value(
        portfolio_id,
        db
    )

    if valuation is None:
        return None

    if not valuation.get("holdings"):
        return None

    total_value = valuation["current_value"]

    # --------------------------------
    # 3. Get latest portfolio return
    # --------------------------------

    returns_result = get_portfolio_returns(
        portfolio_id,
        db
    )

    daily_return = None

    if returns_result is not None:

        returns_df = returns_result["returns"]

        if (
            not returns_df.empty
            and "portfolio_return" in returns_df.columns
        ):
            latest_return = (
                returns_df["portfolio_return"]
                .dropna()
            )

            if not latest_return.empty:
                daily_return = float(
                    latest_return.iloc[-1]
                )

    # --------------------------------
    # 4. Update if snapshot exists
    # --------------------------------

    if existing_snapshot:

        existing_snapshot.total_value = total_value
        existing_snapshot.daily_return = daily_return

        db.commit()
        db.refresh(existing_snapshot)

        return existing_snapshot

    # --------------------------------
    # 5. Otherwise create snapshot
    # --------------------------------

    snapshot = PortfolioSnapshot(
        portfolio_id=portfolio_id,
        snapshot_date=today,
        total_value=total_value,
        daily_return=daily_return
    )

    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return snapshot