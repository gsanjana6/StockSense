from sqlalchemy.orm import Session

from app.models.holding import Holding
from app.services.market_data_service import get_current_price


def calculate_portfolio_value(
    portfolio_id: int,
    db: Session
):
    # Get all holdings belonging to the portfolio
    holdings = db.query(Holding).filter(
        Holding.portfolio_id == portfolio_id
    ).all()

    if not holdings:
        return {
            "portfolio_id": portfolio_id,
            "total_invested": 0,
            "current_value": 0,
            "total_gain_loss": 0,
            "return_percentage": 0,
            "holdings": []
        }

    holding_results = []

    total_invested = 0
    total_current_value = 0

    for holding in holdings:

        current_price = get_current_price(
            holding.ticker,
            db
        )

        if current_price is None:
            continue

        quantity = float(holding.quantity)
        avg_buy_price = float(holding.avg_buy_price)

        invested_amount = (
            quantity * avg_buy_price
        )

        current_value = (
            quantity * current_price
        )

        gain_loss = (
            current_value - invested_amount
        )

        gain_loss_percentage = (
            (gain_loss / invested_amount) * 100
            if invested_amount > 0
            else 0
        )

        total_invested += invested_amount
        total_current_value += current_value

        holding_results.append({
            "ticker": holding.ticker,
            "quantity": quantity,
            "avg_buy_price": round(
                avg_buy_price,
                2
            ),
            "current_price": round(
                current_price,
                2
            ),
            "invested_amount": round(
                invested_amount,
                2
            ),
            "current_value": round(
                current_value,
                2
            ),
            "gain_loss": round(
                gain_loss,
                2
            ),
            "gain_loss_percentage": round(
                gain_loss_percentage,
                2
            )
        })

    total_gain_loss = (
        total_current_value - total_invested
    )

    return_percentage = (
        (total_gain_loss / total_invested) * 100
        if total_invested > 0
        else 0
    )

    return {
        "portfolio_id": portfolio_id,
        "total_invested": round(
            total_invested,
            2
        ),
        "current_value": round(
            total_current_value,
            2
        ),
        "total_gain_loss": round(
            total_gain_loss,
            2
        ),
        "return_percentage": round(
            return_percentage,
            2
        ),
        "holdings": holding_results
    }