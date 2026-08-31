from sqlalchemy.orm import Session

from app.services.portfolio_service import calculate_portfolio_value
from app.services.company_service import get_or_create_company


def calculate_geographic_exposure(
    portfolio_id: int,
    db: Session
):
    valuation = calculate_portfolio_value(
        portfolio_id,
        db
    )

    if valuation is None or not valuation.get("holdings"):
        return None

    total_value = valuation.get("current_value") or 0

    if not total_value:
        return None

    country_totals = {}

    for holding in valuation["holdings"]:
        ticker = holding["ticker"]
        current_value = float(holding.get("current_value") or 0)

        company = get_or_create_company(
            ticker,
            db
        )

        country = (
            company.country
            if company and company.country
            else "Unknown"
        )

        country_totals[country] = (
            country_totals.get(country, 0) + current_value
        )

    exposure = [
        {
            "country": country,
            "weight": round((value / total_value) * 100, 2),
        }
        for country, value in sorted(
            country_totals.items(),
            key=lambda item: item[1],
            reverse=True
        )
    ]

    largest = exposure[0]

    return {
        "exposure": exposure,
        "largest_country": largest["country"],
        "largest_country_weight": largest["weight"],
    }
