import pandas as pd
import yfinance as yf

from sqlalchemy.orm import Session

from app.models.holding import Holding
from app.models.price_cache import PriceCache

from app.services.analytics_service import (
    get_stock_returns,
    calculate_performance_metrics,
    calculate_portfolio_beta,
    calculate_diversification_metrics,
    calculate_health_score
)


# =========================================================
# SIMULATED HEALTH SCORE
# =========================================================

def calculate_simulated_health_score(
    sharpe: float,
    max_drawdown: float,
    beta: float,
    concentration: float
):
    # -------------------------
    # 1. Sharpe Score (0–25)
    # -------------------------

    if sharpe >= 2:
        sharpe_score = 25
    elif sharpe >= 1:
        sharpe_score = 20
    elif sharpe >= 0.5:
        sharpe_score = 15
    elif sharpe >= 0:
        sharpe_score = 10
    else:
        sharpe_score = 0

    # -------------------------
    # 2. Drawdown Score (0–25)
    # -------------------------

    drawdown = abs(max_drawdown)

    if drawdown <= 10:
        drawdown_score = 25
    elif drawdown <= 20:
        drawdown_score = 20
    elif drawdown <= 30:
        drawdown_score = 15
    elif drawdown <= 40:
        drawdown_score = 10
    else:
        drawdown_score = 5

    # -------------------------
    # 3. Beta Score (0–25)
    # -------------------------

    if beta is None:
        beta_score = 0
    elif 0.8 <= beta <= 1.2:
        beta_score = 25
    elif 0.6 <= beta < 0.8 or 1.2 < beta <= 1.4:
        beta_score = 20
    elif 0.4 <= beta < 0.6 or 1.4 < beta <= 1.6:
        beta_score = 15
    else:
        beta_score = 10

    # -------------------------
    # 4. Diversification Score
    # -------------------------

    if concentration <= 0.25:
        diversification_score = 25
    elif concentration <= 0.40:
        diversification_score = 20
    elif concentration <= 0.60:
        diversification_score = 15
    elif concentration <= 0.80:
        diversification_score = 10
    else:
        diversification_score = 5

    # -------------------------
    # Total
    # -------------------------

    total_score = (
        sharpe_score
        + drawdown_score
        + beta_score
        + diversification_score
    )

    if total_score >= 80:
        rating = "Excellent"
    elif total_score >= 65:
        rating = "Good"
    elif total_score >= 50:
        rating = "Moderate"
    else:
        rating = "Needs Attention"

    return {
        "health_score": total_score,
        "rating": rating,
        "components": {
            "risk_adjusted_performance": sharpe_score,
            "drawdown_control": drawdown_score,
            "market_risk": beta_score,
            "diversification": diversification_score
        }
    }


# =========================================================
# SECTOR HELPER
# =========================================================

def get_sector(ticker: str):
    """
    Get sector information from Yahoo Finance.

    Falls back to 'Other' if sector information
    cannot be retrieved.
    """

    try:
        info = yf.Ticker(ticker).info

        sector = info.get("sector")

        if sector:
            return sector

    except Exception as e:
        print(
            f"Sector lookup failed for {ticker}: {e}"
        )

    return "Other"


def calculate_sector_exposure(
    weights
):
    """
    Calculate sector exposure using portfolio weights.
    """

    sector_weights = {}

    for ticker, weight in weights.items():

        sector = get_sector(ticker)

        sector_weights[sector] = (
            sector_weights.get(sector, 0)
            + weight
        )

    if sector_weights:

        largest_sector = max(
            sector_weights,
            key=sector_weights.get
        )

        largest_sector_weight = (
            sector_weights[largest_sector]
        )

    else:

        largest_sector = None
        largest_sector_weight = 0

    return {
        "sector_weights": {
            sector: round(
                float(weight),
                2
            )
            for sector, weight
            in sector_weights.items()
        },
        "largest_sector": largest_sector,
        "largest_sector_weight": round(
            float(largest_sector_weight),
            2
        )
    }


# =========================================================
# SIMULATE PORTFOLIO
# =========================================================

def simulate_portfolio(
    simulated_holdings,
    db: Session,
    benchmark: str = "SPY"
):

    if not simulated_holdings:
        return None

    holding_values = {}
    return_series = {}

    # =====================================================
    # 1. GET VALUE + RETURNS FOR EACH STOCK
    # =====================================================

    for holding in simulated_holdings:

        ticker = holding["ticker"].upper()
        quantity = float(holding["quantity"])

        latest_price = (
            db.query(PriceCache)
            .filter(
                PriceCache.ticker == ticker
            )
            .order_by(
                PriceCache.price_date.desc()
            )
            .first()
        )

        if latest_price is None:

            return {
                "error":
                    f"No cached market data available for {ticker}"
            }

        holding_values[ticker] = (
            quantity
            * float(latest_price.close)
        )

        stock_returns = get_stock_returns(
            ticker,
            db
        )

        if (
            stock_returns is None
            or stock_returns.empty
        ):

            return {
                "error":
                    f"Insufficient historical data for {ticker}"
            }

        return_series[ticker] = (
            stock_returns["return"]
        )

    # =====================================================
    # 2. CALCULATE WEIGHTS
    # =====================================================

    total_value = sum(
        holding_values.values()
    )

    if total_value <= 0:
        return None

    weights = {
        ticker: value / total_value
        for ticker, value
        in holding_values.items()
    }

    # =====================================================
    # 3. ALIGN HISTORICAL RETURNS
    # =====================================================

    returns_df = pd.concat(
        return_series,
        axis=1
    ).dropna()

    if returns_df.empty:

        return {
            "error":
                "No overlapping historical data for simulated holdings"
        }

    # =====================================================
    # 4. PORTFOLIO DAILY RETURN
    # =====================================================

    portfolio_returns = sum(
        returns_df[ticker] * weight
        for ticker, weight
        in weights.items()
    )

    trading_days = 252
    number_of_days = len(
        portfolio_returns
    )

    # =====================================================
    # 5. ANNUALIZED RETURN
    # =====================================================

    cumulative_growth = (
        1 + portfolio_returns
    ).prod()

    annualized_return = (
        cumulative_growth
        ** (
            trading_days
            / number_of_days
        )
    ) - 1

    # =====================================================
    # 6. ANNUALIZED VOLATILITY
    # =====================================================

    annualized_volatility = (
        portfolio_returns.std()
        * (trading_days ** 0.5)
    )

    # =====================================================
    # 7. SHARPE RATIO
    # =====================================================

    risk_free_rate = 0.04

    sharpe_ratio = (
        (
            annualized_return
            - risk_free_rate
        )
        / annualized_volatility
        if annualized_volatility > 0
        else 0
    )

    # =====================================================
    # 8. MAXIMUM DRAWDOWN
    # =====================================================

    cumulative_returns = (
        1 + portfolio_returns
    ).cumprod()

    running_peak = (
        cumulative_returns.cummax()
    )

    drawdown = (
        cumulative_returns
        / running_peak
    ) - 1

    max_drawdown = drawdown.min()

    # =====================================================
    # 9. BETA
    # =====================================================

    benchmark_df = get_stock_returns(
        benchmark,
        db
    )

    beta = None

    if (
        benchmark_df is not None
        and not benchmark_df.empty
    ):

        benchmark_returns = (
            benchmark_df["return"]
        )

        combined = pd.concat(
            [
                portfolio_returns.rename(
                    "portfolio"
                ),
                benchmark_returns.rename(
                    "benchmark"
                )
            ],
            axis=1
        ).dropna()

        if len(combined) >= 2:

            market_variance = (
                combined["benchmark"].var()
            )

            if market_variance != 0:

                beta = (
                    combined["portfolio"]
                    .cov(
                        combined["benchmark"]
                    )
                    / market_variance
                )

    # =====================================================
    # 10. CONCENTRATION
    # =====================================================

    concentration_index = sum(
        weight ** 2
        for weight in weights.values()
    )

    effective_holdings = (
        1 / concentration_index
        if concentration_index > 0
        else 0
    )

    largest_ticker = max(
        weights,
        key=weights.get
    )

    # =====================================================
    # 11. HEALTH SCORE
    # =====================================================

    simulated_health = (
        calculate_simulated_health_score(
            sharpe=float(
                sharpe_ratio
            ),
            max_drawdown=float(
                max_drawdown * 100
            ),
            beta=(
                float(beta)
                if beta is not None
                else None
            ),
            concentration=float(
                concentration_index
            )
        )
    )

    # =====================================================
    # 12. SECTOR EXPOSURE
    # =====================================================

    sector_exposure = (
        calculate_sector_exposure(
            {
                ticker:
                    weight * 100
                for ticker, weight
                in weights.items()
            }
        )
    )

    # =====================================================
    # 13. RETURN SIMULATION
    # =====================================================

    return {

        "total_simulated_value": round(
            float(total_value),
            2
        ),

        "weights": {
            ticker: round(
                float(weight * 100),
                2
            )
            for ticker, weight
            in weights.items()
        },

        "annualized_return": round(
            float(
                annualized_return * 100
            ),
            2
        ),

        "annualized_volatility": round(
            float(
                annualized_volatility * 100
            ),
            2
        ),

        "sharpe_ratio": round(
            float(sharpe_ratio),
            2
        ),

        "max_drawdown": round(
            float(
                max_drawdown * 100
            ),
            2
        ),

        "beta": (
            round(
                float(beta),
                2
            )
            if beta is not None
            else None
        ),

        "concentration_index": round(
            float(
                concentration_index
            ),
            4
        ),

        "effective_holdings": round(
            float(
                effective_holdings
            ),
            2
        ),

        "largest_holding":
            largest_ticker,

        "largest_weight": round(
            float(
                weights[
                    largest_ticker
                ] * 100
            ),
            2
        ),

        "sector_exposure":
            sector_exposure,

        "observations":
            number_of_days,

        "health":
            simulated_health
    }


# =========================================================
# COMPARE CURRENT VS SIMULATED
# =========================================================

def compare_portfolio_simulation(
    portfolio_id: int,
    simulated_holdings,
    db: Session
):

    # =====================================================
    # 1. GET REAL PORTFOLIO HOLDINGS
    # =====================================================

    current_holdings = (
        db.query(Holding)
        .filter(
            Holding.portfolio_id
            == portfolio_id
        )
        .all()
    )

    if not current_holdings:

        return {
            "error":
                "Portfolio has no holdings"
        }

    # =====================================================
    # 2. CREATE TEMPORARY COPY OF REAL PORTFOLIO
    # =====================================================

    combined_holdings = {}

    for holding in current_holdings:

        ticker = holding.ticker.upper()

        combined_holdings[ticker] = (
            combined_holdings.get(
                ticker,
                0
            )
            + float(
                holding.quantity
            )
        )

    # =====================================================
    # 3. ADD HYPOTHETICAL HOLDINGS
    # =====================================================

    for holding in simulated_holdings:

        # Support both Pydantic objects
        # and dictionaries.

        if isinstance(
            holding,
            dict
        ):

            ticker = (
                holding["ticker"]
                .upper()
            )

            quantity = float(
                holding["quantity"]
            )

        else:

            ticker = (
                holding.ticker.upper()
            )

            quantity = float(
                holding.quantity
            )

        # IMPORTANT:
        # If the user already owns this stock,
        # we ADD the hypothetical quantity.

        combined_holdings[ticker] = (
            combined_holdings.get(
                ticker,
                0
            )
            + quantity
        )

    # =====================================================
    # 4. CONVERT TO SIMULATION FORMAT
    # =====================================================

    simulation_holdings = [
        {
            "ticker": ticker,
            "quantity": quantity
        }
        for ticker, quantity
        in combined_holdings.items()
    ]

    # =====================================================
    # 5. RUN SIMULATION
    # =====================================================

    simulated = simulate_portfolio(
        simulation_holdings,
        db
    )

    if simulated is None:
        return None

    if "error" in simulated:
        return simulated

    # =====================================================
    # 6. CURRENT PORTFOLIO ANALYTICS
    # =====================================================

    current_performance = (
        calculate_performance_metrics(
            portfolio_id,
            db
        )
    )

    current_beta = (
        calculate_portfolio_beta(
            portfolio_id,
            db
        )
    )

    current_diversification = (
        calculate_diversification_metrics(
            portfolio_id,
            db
        )
    )

    current_health = (
        calculate_health_score(
            portfolio_id,
            db
        )
    )

    if (
        current_performance is None
        or current_beta is None
        or current_diversification is None
        or current_health is None
    ):

        return {
            "error":
                "Unable to calculate current portfolio analytics"
        }

    # =====================================================
    # 7. CHANGES
    # =====================================================

    score_change = (
        simulated["health"]["health_score"]
        - current_health["health_score"]
    )

    concentration_change = (
        simulated["concentration_index"]
        - current_diversification[
            "concentration_index"
        ]
    )

    sharpe_change = (
        simulated["sharpe_ratio"]
        - current_performance[
            "sharpe_ratio"
        ]
    )

    volatility_change = (
        simulated[
            "annualized_volatility"
        ]
        - current_performance[
            "annualized_volatility"
        ]
    )

    # =====================================================
    # 8. FINAL COMPARISON
    # =====================================================

    return {

        "current": {

            "annualized_return":
                current_performance[
                    "annualized_return"
                ],

            "annualized_volatility":
                current_performance[
                    "annualized_volatility"
                ],

            "sharpe_ratio":
                current_performance[
                    "sharpe_ratio"
                ],

            "max_drawdown":
                current_performance[
                    "max_drawdown"
                ],

            "beta":
                current_beta,

            "concentration_index":
                current_diversification[
                    "concentration_index"
                ],

            "health_score":
                current_health[
                    "health_score"
                ],

            "rating":
                current_health[
                    "rating"
                ]
        },

        "simulated":
            simulated,

        "comparison": {

            "health_score_change":
                score_change,

            "concentration_change":
                round(
                    concentration_change,
                    4
                ),

            "sharpe_change":
                round(
                    sharpe_change,
                    2
                ),

            "volatility_change":
                round(
                    volatility_change,
                    2
                )
        }
    }