from sqlalchemy.orm import Session

from app.services.analytics_service import (
    calculate_performance_metrics,
    calculate_portfolio_beta,
    calculate_diversification_metrics,
    calculate_health_score
)


def generate_portfolio_interpretation(
    portfolio_id: int,
    db: Session
):
    performance = calculate_performance_metrics(
        portfolio_id,
        db
    )

    beta = calculate_portfolio_beta(
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

    if (
        performance is None
        or beta is None
        or diversification is None
        or health is None
    ):
        return None

    strengths = []
    warnings = []
    recommendations = []

    sharpe = performance["sharpe_ratio"]
    drawdown = abs(performance["max_drawdown"])

    concentration = diversification[
        "concentration_index"
    ]

    largest_holding = diversification[
        "largest_holding"
    ]

    largest_weight = diversification[
        "largest_weight"
    ]

    # -------------------------
    # Sharpe Ratio
    # -------------------------

    if sharpe >= 2:
        strengths.append(
            "The portfolio shows strong historical "
            "risk-adjusted performance."
        )

    elif sharpe >= 1:
        strengths.append(
            "The portfolio shows positive historical "
            "risk-adjusted performance."
        )

    elif sharpe < 0:
        warnings.append(
            "Historical returns have not adequately "
            "compensated for the level of risk taken."
        )

    # -------------------------
    # Maximum Drawdown
    # -------------------------

    if drawdown <= 10:
        strengths.append(
            "Historical downside risk has been relatively limited."
        )

    elif drawdown > 30:
        warnings.append(
            "The portfolio has experienced a substantial "
            "historical decline from its previous peak."
        )

        recommendations.append(
            "Review holdings contributing most strongly "
            "to downside risk."
        )

    # -------------------------
    # Beta
    # -------------------------

    if 0.8 <= beta <= 1.2:
        strengths.append(
            "Portfolio sensitivity to broad market movements "
            "is close to the benchmark."
        )

    elif beta > 1.2:
        warnings.append(
            "The portfolio has historically been more sensitive "
            "to market movements than the benchmark."
        )

        recommendations.append(
            "Consider lower-beta assets if reducing market "
            "sensitivity is a priority."
        )

    # -------------------------
    # Concentration
    # -------------------------

    if largest_weight >= 50:
        warnings.append(
            f"{largest_holding} represents {largest_weight:.2f}% "
            "of the portfolio, creating significant "
            "single-position concentration."
        )

        recommendations.append(
            "Consider reducing reliance on the largest holding "
            "and spreading exposure across additional assets."
        )

    elif concentration <= 0.40:
        strengths.append(
            "Portfolio weights show relatively low concentration."
        )

    # -------------------------
    # Overall summary
    # -------------------------

    summary = (
        f"The portfolio has a StockSense Health Score of "
        f"{health['health_score']}/100, rated "
        f"{health['rating']}."
    )

    return {
        "summary": summary,
        "strengths": strengths,
        "warnings": warnings,
        "recommendations": recommendations
    }