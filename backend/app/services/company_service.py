import requests

from app.core.config import settings


def get_company_profile(ticker: str):

    ticker = ticker.upper()

    url = "https://financialmodelingprep.com/stable/profile"

    params = {
        "symbol": ticker,
        "apikey": settings.FMP_API_KEY
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return data

from sqlalchemy.orm import Session

from app.models.company import CompanyMeta


def get_or_create_company(ticker: str, db: Session):

    ticker = ticker.upper()

    # Check if company already exists in the database
    existing_company = db.query(CompanyMeta).filter(
        CompanyMeta.ticker == ticker
    ).first()

    if existing_company:
        return existing_company

    # Fetch company information from FMP
    data = get_company_profile(ticker)

    # Invalid or unknown ticker
    if not data:
        return None

    profile = data[0]

    # Create company record
    new_company = CompanyMeta(
        ticker=profile.get("symbol"),
        company_name=profile.get("companyName"),
        sector=profile.get("sector"),
        country=profile.get("country"),
        market_cap=profile.get("marketCap"),
        description=profile.get("description")
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return new_company


def search_companies_by_name(name: str, limit: int = 10):
    """Search FMP for companies matching a company name."""

    name = name.strip()

    if not name:
        return []

    url = "https://financialmodelingprep.com/stable/search-name"

    params = {
        "query": name,
        "limit": limit,
        "apikey": settings.FMP_API_KEY,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        return []

    return data
