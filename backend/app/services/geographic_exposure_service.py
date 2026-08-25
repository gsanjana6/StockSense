from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.company import CompanyMeta
from app.services.portfolio_service import calculate_portfolio_value


def calculate_geographic_exposure(portfolio_id: int, db: Session):
    """Return portfolio market-value weights grouped by company country.

    Holdings are valued using the same valuation service used by the dashboard,
    so the geographic percentages are based on current portfolio value rather
    than purchase price. Missing company metadata is kept as "Unknown" instead
    of being silently dropped.
    """
    valuation = calculate_portfolio_value(portfolio_id, db)

    if valuation is None or not valuation.get("holdings"):
        return None

    total_value = float(valuation.get("current_value") or 0)
    if total_value <= 0:
        return None

    tickers = [
        str(holding.get("ticker", "")).upper()
        for holding in valuation.get("holdings", [])
        if holding.get("ticker")
    ]

    companies = {
        company.ticker.upper(): company
        for company in db.query(CompanyMeta).filter(CompanyMeta.ticker.in_(tickers)).all()
    }

    country_values = defaultdict(float)
    holding_details = []

    for holding in valuation.get("holdings", []):
        ticker = str(holding.get("ticker", "")).upper()
        current_value = float(holding.get("current_value") or 0)
        company = companies.get(ticker)
        country = (company.country if company and company.country else "Unknown").strip() or "Unknown"

        country_values[country] += current_value
        holding_details.append({
            "ticker": ticker,
            "country": country,
            "current_value": round(current_value, 2),
            "weight": round((current_value / total_value) * 100, 2),
        })

    exposure = [
        {
            "country": country,
            "value": round(value, 2),
            "weight": round((value / total_value) * 100, 2),
        }
        for country, value in sorted(country_values.items(), key=lambda item: item[1], reverse=True)
    ]

    largest = exposure[0] if exposure else None

    return {
        "total_value": round(total_value, 2),
        "country_count": len(exposure),
        "exposure": exposure,
        "largest_country": largest["country"] if largest else None,
        "largest_country_weight": largest["weight"] if largest else 0,
        "holdings": holding_details,
    }
