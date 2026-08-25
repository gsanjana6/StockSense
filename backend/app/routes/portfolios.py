from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.portfolio_service import calculate_portfolio_value
from app.services.exposure_service import calculate_sector_exposure
from app.services.geographic_exposure_service import calculate_geographic_exposure
from app.database.session import get_db
from app.models.portfolio import Portfolio
from app.models.user import User

from app.services.snapshot_service import (
    create_portfolio_snapshot,
    get_portfolio_snapshot_history
)

from app.schemas.simulation import WhatIfRequest
from app.services.simulation_service import (
    compare_portfolio_simulation
)

from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse
)

from app.services.analytics_service import (
    calculate_performance_metrics,
    calculate_portfolio_beta,
    calculate_correlation_matrix,
    calculate_diversification_metrics,
    calculate_health_score,
    get_portfolio_performance_history
)

from app.services.interpretation_service import (
    generate_portfolio_interpretation
)

from app.services.recommendation_service import (
    generate_portfolio_recommendations
)

from app.utils.auth import get_current_user

router = APIRouter(
    prefix="/portfolios",
    tags=["Portfolios"]
)

@router.post(
    "/",
    response_model=PortfolioResponse
)
def create_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_portfolio = Portfolio(
        user_id=current_user.user_id,
        portfolio_name=portfolio.portfolio_name
    )

    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)

    return new_portfolio



@router.get(
    "/",
    response_model=list[PortfolioResponse]
)
def get_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    portfolios = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.user_id
    ).all()

    return portfolios


@router.put(
    "/{portfolio_id}",
    response_model=PortfolioResponse
)
def update_portfolio(
    portfolio_id: int,
    portfolio_update: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if portfolio is None:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    portfolio.portfolio_name = portfolio_update.portfolio_name

    db.commit()
    db.refresh(portfolio)

    return portfolio

@router.delete("/{portfolio_id}")
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if portfolio is None:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    db.delete(portfolio)
    db.commit()

    return {
        "message": "Portfolio deleted successfully"
    }

@router.get("/{portfolio_id}/valuation")
def get_portfolio_valuation(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find portfolio and verify that it belongs to the logged-in user
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    return calculate_portfolio_value(
        portfolio_id,
        db
    )

@router.get("/{portfolio_id}/analytics")
def get_portfolio_analytics(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify portfolio exists and belongs to logged-in user
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    performance = calculate_performance_metrics(
        portfolio_id,
        db
    )

    beta = calculate_portfolio_beta(
        portfolio_id,
        db
    )

    correlation = calculate_correlation_matrix(
        portfolio_id,
        db
    )

    diversification = calculate_diversification_metrics(
        portfolio_id,
        db
    )

    health = calculate_health_score(
        portfolio_id,
        db
    )

    if performance is None:
        raise HTTPException(
            status_code=400,
            detail="Insufficient data for portfolio analytics"
        )

    # Convert pandas correlation matrix into JSON-compatible dictionary
    correlation_data = (
        correlation.round(4).to_dict()
        if correlation is not None
        else {}
    )

    return {
        "portfolio_id": portfolio_id,

        "performance": performance,

        "risk": {
            "beta": beta,
            "correlation_matrix": correlation_data
        },

        "diversification": diversification,

        "health": health
    }

@router.get("/{portfolio_id}/interpretation")
def get_portfolio_interpretation(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify portfolio belongs to logged-in user
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    interpretation = generate_portfolio_interpretation(
        portfolio_id,
        db
    )

    if interpretation is None:
        raise HTTPException(
            status_code=400,
            detail="Insufficient data for portfolio interpretation"
        )

    return {
        "portfolio_id": portfolio_id,
        "interpretation": interpretation
    }

@router.get("/{portfolio_id}/recommendations")
def get_portfolio_recommendations(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify portfolio exists and belongs to logged-in user
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    recommendations = generate_portfolio_recommendations(
        portfolio_id,
        db
    )

    if recommendations is None:
        raise HTTPException(
            status_code=400,
            detail="Unable to generate portfolio recommendations"
        )

    if recommendations.get("status") == "unavailable":
        raise HTTPException(
            status_code=400,
            detail=recommendations.get(
                "message",
                "Insufficient data for portfolio recommendations"
            )
        )

    return recommendations


@router.get("/{portfolio_id}/exposure")
def get_portfolio_exposure(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    exposure = calculate_sector_exposure(
        portfolio_id,
        db
    )

    if exposure is None:
        raise HTTPException(
            status_code=400,
            detail="Insufficient data for exposure analysis"
        )

    return {
        "portfolio_id": portfolio_id,
        "exposure": exposure
    }

@router.get("/{portfolio_id}/geographic-exposure")
def get_portfolio_geographic_exposure(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    exposure = calculate_geographic_exposure(portfolio_id, db)

    if exposure is None:
        raise HTTPException(
            status_code=400,
            detail="Insufficient data for geographic exposure analysis"
        )

    return {
        "portfolio_id": portfolio_id,
        "exposure": exposure["exposure"],
        "largest_country": exposure["largest_country"],
        "largest_country_weight": exposure["largest_country_weight"],
        "country_count": exposure["country_count"],
        "total_value": exposure["total_value"],
        "holdings": exposure["holdings"],
    }


@router.get("/{portfolio_id}/performance")
def get_portfolio_performance(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    performance = get_portfolio_performance_history(
        portfolio_id,
        db
    )

    if performance is None:
        raise HTTPException(
            status_code=400,
            detail="Insufficient data for performance history"
        )

    return {
        "portfolio_id": portfolio_id,
        "performance": performance
    }

@router.post("/{portfolio_id}/simulate")
def simulate_portfolio_changes(
    portfolio_id: int,
    request: WhatIfRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    result = compare_portfolio_simulation(
        portfolio_id,
        request.holdings,
        db
    )

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Unable to simulate portfolio"
        )

    if "error" in result:
        raise HTTPException(
            status_code=400,
            detail=result["error"]
        )

    return {
        "portfolio_id": portfolio_id,
        "simulation": result
    }

@router.post("/{portfolio_id}/snapshots")
def create_snapshot(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    snapshot = create_portfolio_snapshot(
        portfolio_id,
        db
    )

    if snapshot is None:
        raise HTTPException(
            status_code=400,
            detail="Unable to create portfolio snapshot"
        )

    return {
        "snapshot_id": snapshot.snapshot_id,
        "portfolio_id": snapshot.portfolio_id,
        "snapshot_date": snapshot.snapshot_date,
        "total_value": float(snapshot.total_value),
        "daily_return": (
            float(snapshot.daily_return)
            if snapshot.daily_return is not None
            else None
        )
    }


@router.get("/{portfolio_id}/snapshots")
def get_snapshot_history(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    snapshots = get_portfolio_snapshot_history(
        portfolio_id,
        db
    )

    return {
        "portfolio_id": portfolio_id,
        "snapshots": snapshots
    }