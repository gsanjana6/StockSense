import numpy as np
import pandas as pd

from sqlalchemy.orm import Session

from app.models.holding import Holding
from app.models.price_cache import PriceCache

from app.services.analytics_service import get_stock_returns
from app.services.company_service import get_or_create_company


TRADING_DAYS = 252
RISK_FREE_RATE = 0.04


def calculate_drawdown_recovery(returns):
    growth = (1 + returns).cumprod()
    peaks = growth.cummax()
    drawdowns = (growth / peaks) - 1

    if drawdowns.empty:
        return {
            "max_drawdown": 0,
            "peak_date": None,
            "trough_date": None,
            "recovery_date": None,
            "recovery_days": None
        }

    trough_date = drawdowns.idxmin()
    max_drawdown = float(drawdowns.min())

    peak_value = peaks.loc[trough_date]

    peak_candidates = growth.loc[:trough_date]
    peak_date = peak_candidates[
        peak_candidates == peak_value
    ].index[-1]

    recovery_candidates = growth.loc[trough_date:]

    recovered = recovery_candidates[
        recovery_candidates >= peak_value
    ]

    recovery_date = (
        recovered.index[0]
        if not recovered.empty
        else None
    )

    # Count observed trading-day intervals, not calendar days.
    if recovery_date is not None:
        trough_position = returns.index.get_loc(trough_date)
        recovery_position = returns.index.get_loc(recovery_date)

        recovery_days = recovery_position - trough_position
    else:
        recovery_days = None

    return {
        "max_drawdown": round(max_drawdown * 100, 2),
        "peak_date": str(peak_date),
        "trough_date": str(trough_date),
        "recovery_date": (
            str(recovery_date)
            if recovery_date is not None
            else None
        ),
        "recovery_days": recovery_days
    }


def calculate_risk_contributions(returns_df, weights):
    tickers = list(weights.keys())

    if not tickers:
        return {}

    covariance = (
        returns_df[tickers]
        .cov()
        * TRADING_DAYS
    )

    weight_vector = np.array([
        weights[ticker]
        for ticker in tickers
    ])

    covariance_matrix = covariance.values

    portfolio_variance = float(
        weight_vector
        @ covariance_matrix
        @ weight_vector
    )

    portfolio_volatility = np.sqrt(
        max(portfolio_variance, 0)
    )

    if portfolio_volatility == 0:
        return {}

    marginal = (
        covariance_matrix @ weight_vector
    ) / portfolio_volatility

    component = weight_vector * marginal

    result = {}

    for i, ticker in enumerate(tickers):
        result[ticker] = {
            "marginal_contribution_to_risk": round(
                float(marginal[i] * 100), 4
            ),
            "component_risk": round(
                float(component[i] * 100), 4
            ),
            "percentage_risk_contribution": round(
                float(
                    component[i]
                    / portfolio_volatility
                    * 100
                ),
                2
            )
        }

    return result


def calculate_portfolio_metrics(
    values,
    returns_map,
    benchmark_returns
):
    active = {
        ticker: value
        for ticker, value in values.items()
        if value > 0
    }

    total_value = sum(active.values())

    if total_value <= 0:
        return None

    weights = {
        ticker: value / total_value
        for ticker, value in active.items()
    }

    returns_df = pd.concat(
        {
            ticker: returns_map[ticker]
            for ticker in active
        },
        axis=1
    ).dropna()

    if returns_df.empty:
        return None

    weight_series = pd.Series(weights)

    portfolio_returns = (
        returns_df * weight_series
    ).sum(axis=1)

    observations = len(portfolio_returns)

    if observations < 2:
        return None

    cumulative_growth = (
        1 + portfolio_returns
    ).prod()

    annualized_return = (
        cumulative_growth
        ** (TRADING_DAYS / observations)
    ) - 1

    annualized_volatility = (
        portfolio_returns.std()
        * np.sqrt(TRADING_DAYS)
    )

    sharpe = (
        (annualized_return - RISK_FREE_RATE)
        / annualized_volatility
        if annualized_volatility > 0
        else 0
    )

    benchmark_aligned = pd.concat(
        [
            portfolio_returns.rename("portfolio"),
            benchmark_returns.rename("benchmark")
        ],
        axis=1
    ).dropna()

    beta = None

    if len(benchmark_aligned) >= 2:
        variance = benchmark_aligned[
            "benchmark"
        ].var()

        if variance > 0:
            beta = (
                benchmark_aligned["portfolio"].cov(
                    benchmark_aligned["benchmark"]
                ) / variance
            )

    concentration = sum(
        weight ** 2
        for weight in weights.values()
    )

    risk_contributions = (
        calculate_risk_contributions(
            returns_df,
            weights
        )
    )

    drawdown = calculate_drawdown_recovery(
        portfolio_returns
    )

    asset_metrics = []

    for ticker in active:
        stock_returns = returns_df[ticker]

        asset_growth = (
            1 + stock_returns
        ).prod()

        asset_return = (
            asset_growth
            ** (TRADING_DAYS / len(stock_returns))
        ) - 1

        asset_volatility = (
            stock_returns.std()
            * np.sqrt(TRADING_DAYS)
        )

        asset_metrics.append({
            "ticker": ticker,
            "annualized_return": round(
                float(asset_return * 100), 2
            ),
            "annualized_volatility": round(
                float(asset_volatility * 100), 2
            ),
            "weight": round(
                float(weights[ticker] * 100), 2
            )
        })

    correlation = returns_df.corr().round(4)

    return {
        "total_value": round(float(total_value), 2),

        "weights": {
            ticker: round(weight * 100, 2)
            for ticker, weight in weights.items()
        },

        "annualized_return": round(
            float(annualized_return * 100), 2
        ),

        "annualized_volatility": round(
            float(annualized_volatility * 100), 2
        ),

        "sharpe_ratio": round(float(sharpe), 2),

        "beta": (
            round(float(beta), 2)
            if beta is not None
            else None
        ),

        "max_drawdown": drawdown["max_drawdown"],

        "drawdown_recovery": drawdown,

        "concentration_index": round(
            float(concentration), 4
        ),

        "effective_holdings": round(
            1 / concentration if concentration else 0,
            2
        ),

        "correlation_matrix": correlation.to_dict(),

        "risk_contributions": risk_contributions,

        "asset_metrics": asset_metrics,

        "risk_return_scatter": (
            asset_metrics + [{
                "ticker": "PORTFOLIO",
                "annualized_return": round(
                    float(annualized_return * 100), 2
                ),
                "annualized_volatility": round(
                    float(annualized_volatility * 100), 2
                ),
                "weight": 100
            }]
        ),

        "observations": observations
    }


def run_advanced_simulation(
    portfolio_id: int,
    request,
    db: Session
):
    holdings = (
        db.query(Holding)
        .filter(
            Holding.portfolio_id == portfolio_id
        )
        .all()
    )

    if not holdings:
        return {"error": "Portfolio has no holdings"}

    current_values = {}

    for holding in holdings:
        ticker = holding.ticker.upper()

        current_values[ticker] = (
            current_values.get(ticker, 0)
            + float(holding.quantity)
        )

    tickers = set(current_values)

    for change in request.changes:
        tickers.add(change.ticker.upper())

    benchmark = request.benchmark.upper()
    tickers.add(benchmark)

    # Retrieve market data and latest prices.
    prices = {}
    returns_map = {}

    for ticker in tickers:
        company = get_or_create_company(ticker, db)

        if company is None:
            return {
                "error": f"Unable to retrieve metadata for {ticker}"
            }

        stock_returns = get_stock_returns(
            ticker,
            db,
            period=request.period
        )

        if stock_returns is None or stock_returns.empty:
            return {
                "error": (
                    f"Insufficient historical data for {ticker}"
                )
            }

        latest = (
            db.query(PriceCache)
            .filter(PriceCache.ticker == ticker)
            .order_by(PriceCache.price_date.desc())
            .first()
        )

        if latest is None:
            return {
                "error": f"No cached price available for {ticker}"
            }

        prices[ticker] = float(latest.close)
        returns_map[ticker] = stock_returns["return"]

    benchmark_returns = returns_map[benchmark]

    # Convert existing quantities into current market values.
    current_values = {
        ticker: quantity * prices[ticker]
        for ticker, quantity in current_values.items()
    }

    # Start with a copy of the actual portfolio.
    scenario_values = current_values.copy()

    # Apply hypothetical dollar changes.
    for change in request.changes:
        ticker = change.ticker.upper()
        action = change.action
        amount = change.amount

        if amount is not None and change.amount_type == "shares":
            amount = amount * prices[ticker]

        existing_value = scenario_values.get(ticker, 0)

        if action == "add":
            if amount is None:
                return {
                    "error": f"Investment amount required for {ticker}"
                }

            scenario_values[ticker] = (
                existing_value + amount
            )

        elif action == "reduce":
            if amount is None:
                return {
                    "error": f"Reduction amount required for {ticker}"
                }

            if existing_value == 0:
                return {
                    "error": f"{ticker} is not in the portfolio"
                }

            if amount > existing_value:
                return {
                    "error": (
                        f"Cannot reduce {ticker} by more than "
                        "its current simulated value"
                    )
                }

            scenario_values[ticker] = (
                existing_value - amount
            )

        elif action == "remove":
            if existing_value == 0:
                return {
                    "error": f"{ticker} is not in the portfolio"
                }

            scenario_values.pop(ticker)

    scenario_values = {
        ticker: value
        for ticker, value in scenario_values.items()
        if value > 0
    }

    current_metrics = calculate_portfolio_metrics(
        current_values,
        returns_map,
        benchmark_returns
    )

    simulated_metrics = calculate_portfolio_metrics(
        scenario_values,
        returns_map,
        benchmark_returns
    )

    if current_metrics is None or simulated_metrics is None:
        return {
            "error": "Unable to calculate portfolio metrics"
        }

    return {
        "benchmark": benchmark,
        "period": request.period,

        "current": current_metrics,

        "simulated": simulated_metrics,

        "comparison": {
            "investment_value_change": round(
                simulated_metrics["total_value"]
                - current_metrics["total_value"],
                2
            ),

            "return_change": round(
                simulated_metrics["annualized_return"]
                - current_metrics["annualized_return"],
                2
            ),

            "volatility_change": round(
                simulated_metrics["annualized_volatility"]
                - current_metrics["annualized_volatility"],
                2
            ),

            "sharpe_change": round(
                simulated_metrics["sharpe_ratio"]
                - current_metrics["sharpe_ratio"],
                2
            ),

            "beta_change": (
                round(
                    simulated_metrics["beta"]
                    - current_metrics["beta"],
                    2
                )
                if (
                    simulated_metrics["beta"] is not None
                    and current_metrics["beta"] is not None
                )
                else None
            )
        }
    }