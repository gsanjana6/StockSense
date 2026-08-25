from sqlalchemy.orm import Session

from app.services.analytics_service import (
    calculate_performance_metrics,
    calculate_portfolio_beta,
    calculate_diversification_metrics,
    calculate_health_score,
)


def generate_portfolio_recommendations(
    portfolio_id: int,
    db: Session
):
    """
    Generate explainable, rule-based portfolio recommendations
    using the analytics already calculated by StockSense.

    This service does not modify the portfolio.
    """

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
        return {
            "portfolio_id": portfolio_id,
            "status": "unavailable",
            "message": (
                "Insufficient portfolio data to generate "
                "recommendations."
            ),
            "recommendations": []
        }

    recommendations = []

    # =====================================================
    # EXTRACT METRICS
    # =====================================================

    sharpe = float(
        performance.get("sharpe_ratio", 0)
    )

    volatility = float(
        performance.get("annualized_volatility", 0)
    )

    max_drawdown = float(
        performance.get("max_drawdown", 0)
    )

    beta_value = float(beta)

    concentration = float(
        diversification.get(
            "concentration_index",
            0
        )
    )

    effective_holdings = float(
        diversification.get(
            "effective_holdings",
            0
        )
    )

    largest_holding = diversification.get(
        "largest_holding"
    )

    largest_weight = float(
        diversification.get(
            "largest_weight",
            0
        )
    )

    weights = diversification.get(
        "weights",
        {}
    )

    health_score = int(
        health.get(
            "health_score",
            0
        )
    )

    rating = health.get(
        "rating",
        "Unknown"
    )

    # =====================================================
    # 1. CONCENTRATION
    # =====================================================

    if concentration > 0.60:

        recommendations.append({
            "type": "diversification",
            "severity": "high",
            "title": "High Portfolio Concentration",
            "message": (
                f"Your portfolio has a concentration index "
                f"of {concentration:.2f}. A large portion of "
                f"portfolio risk is concentrated in a small "
                f"number of holdings."
            ),
            "metric": {
                "name": "Concentration Index",
                "value": round(
                    concentration,
                    4
                )
            },
            "action": (
                "Consider gradually increasing exposure "
                "to additional holdings or asset groups."
            )
        })

    elif concentration > 0.40:

        recommendations.append({
            "type": "diversification",
            "severity": "medium",
            "title": "Moderate Concentration",
            "message": (
                f"The portfolio concentration index is "
                f"{concentration:.2f}, indicating moderate "
                f"concentration."
            ),
            "metric": {
                "name": "Concentration Index",
                "value": round(
                    concentration,
                    4
                )
            },
            "action": (
                "Consider adding less-correlated holdings "
                "to improve diversification."
            )
        })

    else:

        recommendations.append({
            "type": "diversification",
            "severity": "positive",
            "title": "Healthy Diversification",
            "message": (
                f"The concentration index of "
                f"{concentration:.2f} indicates that the "
                f"portfolio is reasonably diversified."
            ),
            "metric": {
                "name": "Concentration Index",
                "value": round(
                    concentration,
                    4
                )
            },
            "action": (
                "Maintain diversification while monitoring "
                "changes in individual holding weights."
            )
        })

    # =====================================================
    # 2. LARGEST HOLDING
    # =====================================================

    if largest_weight >= 50:

        recommendations.append({
            "type": "holding_concentration",
            "severity": "high",
            "title": "Large Single-Holding Exposure",
            "message": (
                f"{largest_holding} represents "
                f"{largest_weight:.2f}% of the portfolio."
            ),
            "metric": {
                "name": "Largest Holding Weight",
                "value": round(
                    largest_weight,
                    2
                )
            },
            "action": (
                "Consider whether this level of exposure "
                "matches your intended risk tolerance."
            )
        })

    elif largest_weight >= 30:

        recommendations.append({
            "type": "holding_concentration",
            "severity": "medium",
            "title": "Notable Single-Holding Exposure",
            "message": (
                f"{largest_holding} represents "
                f"{largest_weight:.2f}% of the portfolio."
            ),
            "metric": {
                "name": "Largest Holding Weight",
                "value": round(
                    largest_weight,
                    2
                )
            },
            "action": (
                "Monitor the position because movements "
                "in this holding can materially affect "
                "portfolio performance."
            )
        })

    # =====================================================
    # 3. EFFECTIVE HOLDINGS
    # =====================================================

    if effective_holdings < 2:

        recommendations.append({
            "type": "diversification",
            "severity": "high",
            "title": "Limited Effective Diversification",
            "message": (
                f"The portfolio has an effective holding "
                f"count of approximately "
                f"{effective_holdings:.2f}."
            ),
            "metric": {
                "name": "Effective Holdings",
                "value": round(
                    effective_holdings,
                    2
                )
            },
            "action": (
                "Consider broadening the portfolio with "
                "additional holdings."
            )
        })

    # =====================================================
    # 4. VOLATILITY
    # =====================================================

    if volatility > 30:

        recommendations.append({
            "type": "risk",
            "severity": "high",
            "title": "High Portfolio Volatility",
            "message": (
                f"Annualized volatility is "
                f"{volatility:.2f}%, indicating relatively "
                f"large historical fluctuations."
            ),
            "metric": {
                "name": "Annualized Volatility",
                "value": round(
                    volatility,
                    2
                )
            },
            "action": (
                "Consider balancing higher-volatility "
                "holdings with assets that have historically "
                "shown lower volatility."
            )
        })

    elif volatility > 20:

        recommendations.append({
            "type": "risk",
            "severity": "medium",
            "title": "Moderate-to-High Volatility",
            "message": (
                f"Annualized volatility is "
                f"{volatility:.2f}%, so portfolio values "
                f"may experience noticeable fluctuations."
            ),
            "metric": {
                "name": "Annualized Volatility",
                "value": round(
                    volatility,
                    2
                )
            },
            "action": (
                "Monitor volatility alongside your investment "
                "horizon and risk tolerance."
            )
        })

    else:

        recommendations.append({
            "type": "risk",
            "severity": "positive",
            "title": "Controlled Volatility",
            "message": (
                f"Annualized volatility is "
                f"{volatility:.2f}%, indicating relatively "
                f"controlled historical fluctuations."
            ),
            "metric": {
                "name": "Annualized Volatility",
                "value": round(
                    volatility,
                    2
                )
            },
            "action": (
                "Continue monitoring volatility as market "
                "conditions and portfolio weights change."
            )
        })

    # =====================================================
    # 5. BETA / MARKET SENSITIVITY
    # =====================================================

    if beta_value > 1.30:

        recommendations.append({
            "type": "market_risk",
            "severity": "high",
            "title": "High Market Sensitivity",
            "message": (
                f"Portfolio beta is {beta_value:.2f}, "
                f"indicating greater sensitivity to broad "
                f"market movements."
            ),
            "metric": {
                "name": "Beta",
                "value": round(
                    beta_value,
                    2
                )
            },
            "action": (
                "Consider whether the portfolio's market "
                "sensitivity is appropriate for your risk "
                "tolerance."
            )
        })

    elif beta_value > 1.10:

        recommendations.append({
            "type": "market_risk",
            "severity": "medium",
            "title": "Elevated Market Sensitivity",
            "message": (
                f"Portfolio beta is {beta_value:.2f}, "
                f"so the portfolio may move more than the "
                f"benchmark during broad market movements."
            ),
            "metric": {
                "name": "Beta",
                "value": round(
                    beta_value,
                    2
                )
            },
            "action": (
                "Monitor market sensitivity when making "
                "additional high-beta investments."
            )
        })

    else:

        recommendations.append({
            "type": "market_risk",
            "severity": "positive",
            "title": "Balanced Market Sensitivity",
            "message": (
                f"Portfolio beta is {beta_value:.2f}, "
                f"which indicates relatively balanced "
                f"sensitivity to the benchmark."
            ),
            "metric": {
                "name": "Beta",
                "value": round(
                    beta_value,
                    2
                )
            },
            "action": (
                "Maintain awareness of beta as portfolio "
                "composition changes."
            )
        })

    # =====================================================
    # 6. MAXIMUM DRAWDOWN
    # =====================================================

    drawdown = abs(
        max_drawdown
    )

    if drawdown > 30:

        recommendations.append({
            "type": "downside_risk",
            "severity": "high",
            "title": "Significant Historical Drawdown",
            "message": (
                f"The portfolio experienced a maximum "
                f"historical drawdown of "
                f"{drawdown:.2f}%."
            ),
            "metric": {
                "name": "Maximum Drawdown",
                "value": round(
                    max_drawdown,
                    2
                )
            },
            "action": (
                "Review position sizing and downside "
                "tolerance before increasing portfolio risk."
            )
        })

    elif drawdown > 20:

        recommendations.append({
            "type": "downside_risk",
            "severity": "medium",
            "title": "Meaningful Historical Drawdown",
            "message": (
                f"The maximum historical drawdown was "
                f"{drawdown:.2f}%."
            ),
            "metric": {
                "name": "Maximum Drawdown",
                "value": round(
                    max_drawdown,
                    2
                )
            },
            "action": (
                "Keep downside risk in mind when evaluating "
                "new positions."
            )
        })

    else:

        recommendations.append({
            "type": "downside_risk",
            "severity": "positive",
            "title": "Manageable Historical Drawdown",
            "message": (
                f"The maximum historical drawdown was "
                f"{drawdown:.2f}%, which is relatively "
                f"manageable."
            ),
            "metric": {
                "name": "Maximum Drawdown",
                "value": round(
                    max_drawdown,
                    2
                )
            },
            "action": (
                "Continue monitoring downside behaviour "
                "during changing market conditions."
            )
        })

    # =====================================================
    # 7. SHARPE RATIO
    # =====================================================

    if sharpe < 0:

        recommendations.append({
            "type": "risk_adjusted_performance",
            "severity": "high",
            "title": "Weak Risk-Adjusted Performance",
            "message": (
                f"The Sharpe ratio is {sharpe:.2f}, "
                f"indicating that historical returns have "
                f"not adequately compensated for portfolio risk."
            ),
            "metric": {
                "name": "Sharpe Ratio",
                "value": round(
                    sharpe,
                    2
                )
            },
            "action": (
                "Review whether the current risk level is "
                "justified by historical returns."
            )
        })

    elif sharpe < 1:

        recommendations.append({
            "type": "risk_adjusted_performance",
            "severity": "medium",
            "title": "Moderate Risk-Adjusted Performance",
            "message": (
                f"The Sharpe ratio is {sharpe:.2f}, "
                f"indicating moderate compensation for "
                f"the portfolio risk taken."
            ),
            "metric": {
                "name": "Sharpe Ratio",
                "value": round(
                    sharpe,
                    2
                )
            },
            "action": (
                "Consider whether portfolio risk can be "
                "reduced without materially affecting returns."
            )
        })

    else:

        recommendations.append({
            "type": "risk_adjusted_performance",
            "severity": "positive",
            "title": "Strong Risk-Adjusted Performance",
            "message": (
                f"The Sharpe ratio is {sharpe:.2f}, "
                f"indicating strong historical risk-adjusted "
                f"performance."
            ),
            "metric": {
                "name": "Sharpe Ratio",
                "value": round(
                    sharpe,
                    2
                )
            },
            "action": (
                "Continue monitoring whether this performance "
                "persists as market conditions change."
            )
        })

    # =====================================================
    # 8. OVERALL ASSESSMENT
    # =====================================================

    if health_score >= 80:

        overall_message = (
            f"Your portfolio is currently rated "
            f"{rating} with a health score of "
            f"{health_score}/100. The portfolio is in "
            f"strong overall condition; focus on maintaining "
            f"diversification and monitoring risk."
        )

    elif health_score >= 65:

        overall_message = (
            f"Your portfolio is currently rated "
            f"{rating} with a health score of "
            f"{health_score}/100. The portfolio is generally "
            f"healthy, but some risk areas may benefit from "
            f"attention."
        )

    elif health_score >= 50:

        overall_message = (
            f"Your portfolio is currently rated "
            f"{rating} with a health score of "
            f"{health_score}/100. Several areas could be "
            f"improved through diversification or risk "
            f"management."
        )

    else:

        overall_message = (
            f"Your portfolio is currently rated "
            f"{rating} with a health score of "
            f"{health_score}/100. The portfolio has "
            f"significant areas that require attention."
        )

    # =====================================================
    # 9. RETURN
    # =====================================================

    return {
        "portfolio_id": portfolio_id,

        "status": "success",

        "overall_assessment": {
            "health_score": health_score,
            "rating": rating,
            "message": overall_message
        },

        "portfolio_metrics": {
            "sharpe_ratio": round(
                sharpe,
                2
            ),
            "annualized_volatility": round(
                volatility,
                2
            ),
            "max_drawdown": round(
                max_drawdown,
                2
            ),
            "beta": round(
                beta_value,
                2
            ),
            "concentration_index": round(
                concentration,
                4
            ),
            "effective_holdings": round(
                effective_holdings,
                2
            ),
            "largest_holding": largest_holding,
            "largest_weight": round(
                largest_weight,
                2
            ),
            "weights": weights
        },

        "recommendations": recommendations,

        "recommendation_count":
            len(recommendations)
    }