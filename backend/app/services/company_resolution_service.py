
import logging
import re

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.company import CompanyMeta
from app.services.company_service import (
    get_or_create_company,
    search_companies_by_name,
)

logger = logging.getLogger(__name__)


COMPANY_ALIASES = {
    "apple": "Apple Inc.",
    "microsoft": "Microsoft Corporation",
    "nvidia": "NVIDIA Corporation",
    "tesla": "Tesla, Inc.",
}


def normalize_company_name(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^\w\s]", " ", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()


def format_candidate(item: dict) -> dict:
    return {
        "ticker": item.get("symbol"),
        "company_name": item.get("name") or item.get("companyName"),
        "exchange": item.get("exchangeFullName") or item.get("exchange"),
    }


def prefer_primary_us_listing(candidates: list[dict]) -> list[dict]:
    us_candidates = [
        candidate
        for candidate in candidates
        if any(
            exchange in (candidate.get("exchange") or "").upper()
            for exchange in [
                "NASDAQ",
                "NEW YORK STOCK EXCHANGE",
                "NYSE",
            ]
        )
    ]

    if len(us_candidates) == 1:
        return us_candidates

    return candidates


def _result(status, ticker=None, company_name=None, candidates=None):
    return {
        "status": status,
        "ticker": ticker,
        "company_name": company_name,
        "candidates": candidates or [],
    }


def resolve_company_reference(reference: str, db: Session) -> dict:
    if not reference or not reference.strip():
        return _result("not_found")

    reference = reference.strip()
    normalized = normalize_company_name(reference)

    # 1. Exact ticker lookup.
    ticker_match = db.query(CompanyMeta).filter(
        func.upper(CompanyMeta.ticker) == reference.upper()
    ).first()

    if ticker_match:
        return _result(
            "matched",
            ticker_match.ticker,
            ticker_match.company_name
        )

    # 2. Exact local company-name lookup.
    local_companies = db.query(CompanyMeta).all()

    exact_matches = [
        company for company in local_companies
        if normalize_company_name(company.company_name) == normalized
    ]

    if len(exact_matches) == 1:
        company = exact_matches[0]
        return _result("matched", company.ticker, company.company_name)

    if len(exact_matches) > 1:
        return _result(
            "ambiguous",
            candidates=[
                {
                    "ticker": company.ticker,
                    "company_name": company.company_name
                }
                for company in exact_matches
            ]
        )

    # 3. Common company aliases.
    alias = COMPANY_ALIASES.get(normalized)

    if alias:
        alias_normalized = normalize_company_name(alias)

        alias_matches = [
            company for company in local_companies
            if normalize_company_name(company.company_name) == alias_normalized
        ]

        if len(alias_matches) == 1:
            company = alias_matches[0]
            return _result("matched", company.ticker, company.company_name)

    # 4. Partial local company-name lookup.
    partial_matches = db.query(CompanyMeta).filter(
        CompanyMeta.company_name.ilike(f"%{reference}%")
    ).limit(10).all()

    if len(partial_matches) == 1:
        company = partial_matches[0]
        return _result("matched", company.ticker, company.company_name)

    if len(partial_matches) > 1:
        return _result(
            "ambiguous",
            candidates=[
                {
                    "ticker": company.ticker,
                    "company_name": company.company_name
                }
                for company in partial_matches
            ]
        )

    # 5. External FMP lookup only when local resolution fails.
    try:
        results = search_companies_by_name(reference, limit=10)

        candidates = [
            format_candidate(item)
            for item in results
            if item.get("symbol")
            and (item.get("name") or item.get("companyName"))
            and (item.get("exchange") or "").upper() != "CRYPTO"
        ]

        exact_external = [
            candidate for candidate in candidates
            if normalize_company_name(candidate["company_name"]) == normalized
        ]

        if exact_external:
            candidates = exact_external

        candidates = prefer_primary_us_listing(candidates)

        unique_candidates = {}

        for candidate in candidates:
            unique_candidates[candidate["ticker"]] = candidate

        candidates = list(unique_candidates.values())

        if len(candidates) == 1:
            verified = get_or_create_company(
                candidates[0]["ticker"],
                db
            )

            if verified:
                return _result(
                    "matched",
                    verified.ticker,
                    verified.company_name
                )

        if len(candidates) > 1:
            return _result("ambiguous", candidates=candidates)

    except Exception:
        logger.exception(
            "FMP company-name search failed for %s",
            reference
        )

    return _result("not_found")


def extract_company_references(message: str, db: Session) -> list[str]:
    """
    Extract likely company names from a user message.

    Checks locally known company names first, then common aliases,
    then simple company-name phrases around relevant keywords.
    Does not make external API requests.
    """
    if not message:
        return []

    message_lower = message.lower()
    references = []

    def add_reference(value):
        value = value.strip(" \t\n.,?!:;()[]{}'\"")
        normalized = normalize_company_name(value)

        if normalized and normalized not in {
            normalize_company_name(item) for item in references
        }:
            references.append(value)

    # 1. Match companies already stored locally.
    companies = db.query(CompanyMeta).all()

    for company in companies:
        name = company.company_name

        if re.search(
            rf"(?<!\w){re.escape(name)}(?!\w)",
            message,
            flags=re.IGNORECASE
        ):
            add_reference(name)

    # 2. Match common aliases.
    for alias in COMPANY_ALIASES:
        if re.search(
            rf"(?<!\w){re.escape(alias)}(?!\w)",
            message_lower
        ):
            add_reference(alias)

    # 3. Extract company names in possessive phrases.
    possessive_pattern = (
        r"\b([A-Z][A-Za-z0-9&.-]*"
        r"(?:\s+[A-Z][A-Za-z0-9&.-]*){0,3})"
        r"['’]s\b"
    )

    for match in re.finditer(possessive_pattern, message):
        add_reference(match.group(1))

    # 4. Extract names following relevant keywords.
    keyword_pattern = (
        r"\b(?:of|about|for|regarding|analyse|analyze|"
        r"compare|between|versus|vs)\s+"
        r"([A-Z][A-Za-z0-9&.-]*"
        r"(?:\s+[A-Z][A-Za-z0-9&.-]*){0,2})"
    )

    for match in re.finditer(keyword_pattern, message):
        candidate = match.group(1)

        if candidate.lower() not in {
            "my portfolio",
            "the portfolio",
            "the market",
            "the stock market",
            "the s",
        }:
            add_reference(candidate)

    return references


def resolve_explicit_ticker(ticker: str, db: Session) -> dict:
    if not ticker:
        return _result("not_found")

    ticker = ticker.strip().upper()

    if not re.fullmatch(r"[A-Z0-9.-]{1,15}", ticker):
        return _result("not_found")

    # Avoid unnecessary FMP calls for known tickers.
    existing = db.query(CompanyMeta).filter(
        func.upper(CompanyMeta.ticker) == ticker
    ).first()

    if existing:
        return _result(
            "matched",
            existing.ticker,
            existing.company_name
        )

    try:
        company = get_or_create_company(ticker, db)

        if company:
            return _result(
                "matched",
                company.ticker,
                company.company_name
            )

    except Exception:
        logger.exception("Ticker verification failed for %s", ticker)

    return _result("not_found")
