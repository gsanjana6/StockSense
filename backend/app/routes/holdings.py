from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.models.holding import Holding
from app.models.portfolio import Portfolio
from app.models.user import User

from app.schemas.holding import (
    HoldingCreate,
    HoldingUpdate,
    HoldingResponse
)

from app.utils.auth import get_current_user
from app.services.company_service import get_or_create_company


router = APIRouter(
    prefix="/portfolios",
    tags=["Holdings"]
)

@router.post(
    "/{portfolio_id}/holdings",
    response_model=HoldingResponse
)
def create_holding(
    portfolio_id: int,
    holding: HoldingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check that the portfolio exists AND belongs to the logged-in user
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if portfolio is None:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    # Check whether this ticker already exists in this portfolio
    existing_holding = db.query(Holding).filter(
        Holding.portfolio_id == portfolio_id,
        Holding.ticker == holding.ticker.upper()
    ).first()

    if existing_holding:
        raise HTTPException(
            status_code=400,
            detail="This stock already exists in the portfolio"
        )

    # Fetch and store company metadata if it does not already exist
    company = get_or_create_company(
        holding.ticker,
        db
    )

    if company is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid stock ticker"
        )

    # Create the holding
    new_holding = Holding(
        portfolio_id=portfolio_id,
        ticker=holding.ticker.upper(),
        quantity=holding.quantity,
        avg_buy_price=holding.avg_buy_price
    )

    db.add(new_holding)
    db.commit()
    db.refresh(new_holding)

    return new_holding

@router.get(
    "/{portfolio_id}/holdings",
    response_model=list[HoldingResponse]
)
def get_holdings(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check that the portfolio belongs to the logged-in user
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if portfolio is None:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    # Get all holdings inside this portfolio
    holdings = db.query(Holding).filter(
        Holding.portfolio_id == portfolio_id
    ).all()

    return holdings

@router.put(
    "/{portfolio_id}/holdings/{holding_id}",
    response_model=HoldingResponse
)
def update_holding(
    portfolio_id: int,
    holding_id: int,
    holding_update: HoldingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check that the portfolio belongs to the logged-in user
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if portfolio is None:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    # Find the holding inside this portfolio
    holding = db.query(Holding).filter(
        Holding.holding_id == holding_id,
        Holding.portfolio_id == portfolio_id
    ).first()

    if holding is None:
        raise HTTPException(
            status_code=404,
            detail="Holding not found"
        )

    # Update the values
    holding.quantity = holding_update.quantity
    holding.avg_buy_price = holding_update.avg_buy_price

    db.commit()
    db.refresh(holding)

    return holding

@router.delete(
    "/{portfolio_id}/holdings/{holding_id}"
)
def delete_holding(
    portfolio_id: int,
    holding_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check that the portfolio belongs to the logged-in user
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if portfolio is None:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    # Find the holding inside this portfolio
    holding = db.query(Holding).filter(
        Holding.holding_id == holding_id,
        Holding.portfolio_id == portfolio_id
    ).first()

    if holding is None:
        raise HTTPException(
            status_code=404,
            detail="Holding not found"
        )

    db.delete(holding)
    db.commit()

    return {
        "message": "Holding deleted successfully"
    }