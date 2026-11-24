
import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.services.market_data_service import get_current_price


TICKER_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9.-]{0,14}$")


def validate_ticker(ticker: str, db: Session) -> str:
    if not ticker:
        raise HTTPException(
            status_code=400,
            detail="A stock ticker is required."
        )

    ticker = ticker.strip().upper()

    if not TICKER_PATTERN.fullmatch(ticker):
        raise HTTPException(
            status_code=400,
            detail="Invalid ticker format."
        )

    price = get_current_price(ticker, db)

    if price is None or price <= 0:
        raise HTTPException(
            status_code=404,
            detail=f"No market data is available for {ticker}."
        )

    return ticker


def validate_portfolio_access(
    portfolio_id: int,
    user_id: int,
    db: Session
) -> Portfolio:
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == user_id
    ).first()

    if portfolio is None:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found."
        )

    return portfolio


def validate_intent_parameters(
    intent_result,
    user_id: int,
    db: Session
):
    if intent_result.portfolio_id is not None:
        validate_portfolio_access(
            portfolio_id=intent_result.portfolio_id,
            user_id=user_id,
            db=db
        )

    # Validate every extracted ticker, not just the first one.
    tickers = list(dict.fromkeys(
        ticker.strip().upper()
        for ticker in (
            (intent_result.tickers or [])
            + ([intent_result.ticker] if intent_result.ticker else [])
        )
        if ticker and ticker.strip()
    ))

    validated_tickers = []

    for ticker in tickers:
        validated_tickers.append(
            validate_ticker(ticker, db)
        )

    intent_result.tickers = validated_tickers
    intent_result.ticker = (
        validated_tickers[0] if validated_tickers else None
    )

    return intent_result
