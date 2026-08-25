from sqlalchemy.orm import Session

from app.models.holding import Holding
from app.models.company import CompanyMeta
from app.models.price_cache import PriceCache


def calculate_sector_exposure(
    portfolio_id: int,
    db: Session
):
    holdings = db.query(Holding).filter(
        Holding.portfolio_id == portfolio_id
    ).all()

    if not holdings:
        return None

    sector_values = {}
    total_portfolio_value = 0

    for holding in holdings:
        ticker = holding.ticker.upper()

        # Get company metadata
        company = db.query(CompanyMeta).filter(
            CompanyMeta.ticker == ticker
        ).first()

        # Get latest cached price
        latest_price = (
            db.query(PriceCache)
            .filter(PriceCache.ticker == ticker)
            .order_by(PriceCache.price_date.desc())
            .first()
        )

        if latest_price is None:
            continue

        holding_value = (
            float(holding.quantity)
            * float(latest_price.close)
        )

        total_portfolio_value += holding_value

        # Use Unknown if sector metadata is unavailable
        sector = (
            company.sector
            if company and company.sector
            else "Unknown"
        )

        sector_values[sector] = (
            sector_values.get(sector, 0)
            + holding_value
        )

    if total_portfolio_value == 0:
        return None

    sector_exposure = {
        sector: round(
            float(
                value / total_portfolio_value * 100
            ),
            2
        )
        for sector, value in sector_values.items()
    }

    largest_sector = max(
        sector_exposure,
        key=sector_exposure.get
    )

    return {
        "sector_exposure": sector_exposure,
        "largest_sector": largest_sector,
        "largest_sector_weight": sector_exposure[
            largest_sector
        ],
        "sector_count": len(sector_exposure)
    }