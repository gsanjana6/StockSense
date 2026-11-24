
from app.services.company_resolution_service import (
    resolve_company_reference,
    resolve_explicit_ticker,
)
from app.database.session import SessionLocal


db = SessionLocal()

try:
    test_references = [
        "AAPL",
        "Apple",
        "MSFT",
        "Microsoft",
        "Tesla",
        "NVIDIA",
        "UnknownCompanyXYZ",
    ]

    for reference in test_references:
        result = resolve_company_reference(reference, db)

        print("\nReference:", reference)
        print("Status:", result["status"])
        print("Ticker:", result["ticker"])
        print("Company:", result["company_name"])
        print("Candidates:", result["candidates"])

finally:
    db.close()
