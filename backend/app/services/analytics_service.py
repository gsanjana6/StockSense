
import logging

import pandas as pd
from sqlalchemy.orm import Session

from app.models.holding import Holding
from app.models.price_cache import PriceCache
from app.services.market_data_service import (
    get_current_price,
    get_historical_prices,
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# STOCK RETURNS
# --------------------------------------------------

def get_stock_returns(
    ticker: str,
    db: Session,
    period: str = "1y"
):
    ticker = ticker.strip().upper()

    if not ticker:
        return None

    prices = get_historical_prices(
        ticker=ticker,
        period=period,
        db=db
    )

    if prices is None or prices.empty or "Close" not in prices.columns:
        return None

    prices = prices[["Close"]].copy()
    prices["Close"] = pd.to_numeric(
        prices["Close"],
        errors="coerce"
    )

    prices.dropna(subset=["Close"], inplace=True)

    if len(prices) < 2:
        return None

    prices["return"] = prices["Close"].pct_change()
    prices.dropna(subset=["return"], inplace=True)

    if prices.empty:
        return None

    return prices.rename(columns={"Close": "close"})


# --------------------------------------------------
# PORTFOLIO RETURNS
# --------------------------------------------------

def get_portfolio_returns(
    portfolio_id: int,
    db: Session,
    period: str = "1y"
):
    holdings = (
        db.query(Holding)
        .filter(Holding.portfolio_id == portfolio_id)
        .all()
    )

    if not holdings:
        return None

    # Aggregate multiple entries for the same ticker.
    quantities = {}

    for holding in holdings:
        ticker = holding.ticker.strip().upper()

        quantities[ticker] = (
            quantities.get(ticker, 0.0)
            + float(holding.quantity)
        )

    returns_data = {}
    holding_values = {}
    missing_tickers = []

    for ticker, quantity in quantities.items():

        stock_returns = get_stock_returns(
            ticker=ticker,
            db=db,
            period=period
        )

        if stock_returns is None or stock_returns.empty:
            missing_tickers.append(ticker)
            continue

        current_price = get_current_price(ticker, db)

        if current_price is None or current_price <= 0:
            missing_tickers.append(ticker)
            continue

        current_value = quantity * current_price

        if current_value <= 0:
            missing_tickers.append(ticker)
            continue

        holding_values[ticker] = current_value
        returns_data[ticker] = stock_returns["return"]

    # Do not silently calculate using incomplete holdings.
    if missing_tickers:
        logger.warning(
            "Portfolio %s has unavailable market data for: %s",
            portfolio_id,
            ", ".join(missing_tickers)
        )
        return None

    if not returns_data:
        return None

    # Align all holdings by common trading dates.
    returns_df = pd.DataFrame(returns_data).dropna()

    if returns_df.empty:
        return None

    total_value = sum(holding_values.values())

    if total_value <= 0:
        return None

    # Calculate portfolio weights using current market values.
    weights = {
        ticker: value / total_value
        for ticker, value in holding_values.items()
    }

    # Calculate weighted daily portfolio returns.
    returns_df["portfolio_return"] = sum(
        returns_df[ticker] * weights[ticker]
        for ticker in returns_data
    )

    return {
        "returns": returns_df,
        "weights": weights,
        "holdings_count": len(quantities),
        "data_complete": True,
        "missing_tickers": [],
        "period": period
    }


# --------------------------------------------------
# PERFORMANCE METRICS
# --------------------------------------------------

def calculate_performance_metrics(
    portfolio_id: int,
    db: Session,
    period: str = "1y"
):
    result = get_portfolio_returns(
        portfolio_id,
        db,
        period
    )

    if result is None:
        return None

    portfolio_returns = result["returns"]["portfolio_return"]

    if portfolio_returns.empty:
        return None

    trading_days = 252

    # Annualized return using compounded daily returns.
    cumulative_growth = (1 + portfolio_returns).prod()

    number_of_days = len(portfolio_returns)

    if number_of_days == 0 or cumulative_growth <= 0:
        return None

    annualized_return = (
        cumulative_growth ** (trading_days / number_of_days)
    ) - 1

    # Annualized volatility.
    annualized_volatility = (
        portfolio_returns.std() * (trading_days ** 0.5)
    )

    # Risk-free rate assumption: 4% annually.
    risk_free_rate = 0.04

    # Sharpe Ratio.
    sharpe_ratio = (
        (annualized_return - risk_free_rate) / annualized_volatility
        if pd.notna(annualized_volatility)
        and annualized_volatility > 0
        else 0
    )

    # Cumulative portfolio growth.
    cumulative_returns = (1 + portfolio_returns).cumprod()

    # Running portfolio peak.
    running_peak = cumulative_returns.cummax()

    # Drawdown from previous peak.
    drawdown = (cumulative_returns / running_peak) - 1

    # Maximum Drawdown.
    max_drawdown = drawdown.min()

    return {
        "annualized_return": round(
            float(annualized_return * 100), 2
        ),
        "annualized_volatility": round(
            float(annualized_volatility * 100), 2
        ),
        "sharpe_ratio": round(
            float(sharpe_ratio), 2
        ),
        "max_drawdown": round(
            float(max_drawdown * 100), 2
        ),
        "observations": number_of_days,
        "period": period,
        "data_complete": result["data_complete"]
    }


# --------------------------------------------------
# PORTFOLIO BETA
# --------------------------------------------------

def calculate_portfolio_beta(
    portfolio_id: int,
    db: Session,
    benchmark: str = "SPY",
    period: str = "1y"
):
    portfolio_result = get_portfolio_returns(
        portfolio_id,
        db,
        period
    )

    if portfolio_result is None:
        return None

    portfolio_returns = (
        portfolio_result["returns"]["portfolio_return"]
    )

    benchmark_returns_df = get_stock_returns(
        benchmark,
        db,
        period
    )

    if benchmark_returns_df is None:
        return None

    benchmark_returns = benchmark_returns_df["return"]

    # Align portfolio and benchmark returns by date.
    combined = pd.concat(
        [
            portfolio_returns.rename("portfolio"),
            benchmark_returns.rename("benchmark")
        ],
        axis=1
    ).dropna()

    if len(combined) < 2:
        return None

    covariance = combined["portfolio"].cov(
        combined["benchmark"]
    )

    market_variance = combined["benchmark"].var()

    if pd.isna(market_variance) or market_variance == 0:
        return None

    beta = covariance / market_variance

    return round(float(beta), 2)


# --------------------------------------------------
# CORRELATION MATRIX
# --------------------------------------------------

def calculate_correlation_matrix(
    portfolio_id: int,
    db: Session,
    period: str = "1y"
):
    result = get_portfolio_returns(
        portfolio_id,
        db,
        period
    )

    if result is None:
        return None

    returns_df = result["returns"].copy()

    stock_returns = returns_df.drop(
        columns=["portfolio_return"],
        errors="ignore"
    )

    if stock_returns.empty:
        return None

    return stock_returns.corr()


# --------------------------------------------------
# DIVERSIFICATION METRICS
# --------------------------------------------------

def calculate_diversification_metrics(
    portfolio_id: int,
    db: Session,
    period: str = "1y"
):
    result = get_portfolio_returns(
        portfolio_id,
        db,
        period
    )

    if result is None:
        return None

    weights = result["weights"]

    if not weights:
        return None

    # Herfindahl-Hirschman Index.
    concentration_index = sum(
        weight ** 2
        for weight in weights.values()
    )

    # Effective number of equally weighted holdings.
    effective_holdings = (
        1 / concentration_index
        if concentration_index > 0
        else 0
    )

    # Largest position in the portfolio.
    largest_ticker = max(
        weights,
        key=weights.get
    )

    largest_weight = weights[largest_ticker]

    return {
        "concentration_index": round(
            float(concentration_index), 4
        ),
        "effective_holdings": round(
            float(effective_holdings), 2
        ),
        "largest_holding": largest_ticker,
        "largest_weight": round(
            float(largest_weight * 100), 2
        ),
        "weights": {
            ticker: round(float(weight * 100), 2)
            for ticker, weight in weights.items()
        },
        "data_complete": result["data_complete"]
    }


# --------------------------------------------------
# PORTFOLIO HEALTH SCORE
# --------------------------------------------------

def calculate_health_score(
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

    if (
        performance is None
        or beta is None
        or diversification is None
    ):
        return None

    sharpe = performance["sharpe_ratio"]

    max_drawdown = abs(
        performance["max_drawdown"]
    )

    concentration = diversification["concentration_index"]

    # Sharpe Score (0–25).
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

    # Drawdown Score (0–25).
    if max_drawdown <= 10:
        drawdown_score = 25
    elif max_drawdown <= 20:
        drawdown_score = 20
    elif max_drawdown <= 30:
        drawdown_score = 15
    elif max_drawdown <= 40:
        drawdown_score = 10
    else:
        drawdown_score = 5

    # Beta Score (0–25).
    if 0.8 <= beta <= 1.2:
        beta_score = 25
    elif 0.6 <= beta < 0.8 or 1.2 < beta <= 1.4:
        beta_score = 20
    elif 0.4 <= beta < 0.6 or 1.4 < beta <= 1.6:
        beta_score = 15
    else:
        beta_score = 10

    # Concentration Score (0–25).
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
        },
        "metrics": {
            "sharpe_ratio": sharpe,
            "max_drawdown": performance["max_drawdown"],
            "beta": beta,
            "concentration_index": concentration
        }
    }


# --------------------------------------------------
# PORTFOLIO PERFORMANCE HISTORY
# --------------------------------------------------

def get_portfolio_performance_history(
    portfolio_id: int,
    db: Session,
    period: str = "1y"
):
    result = get_portfolio_returns(
        portfolio_id,
        db,
        period
    )

    if result is None:
        return None

    returns_df = result["returns"].copy()

    if returns_df.empty:
        return None

    portfolio_returns = returns_df[
        "portfolio_return"
    ].dropna()

    if portfolio_returns.empty:
        return None

    # Start portfolio growth at 100.
    portfolio_growth = (
        (1 + portfolio_returns).cumprod() * 100
    )

    # Get SPY benchmark returns.
    benchmark_df = get_stock_returns(
        "SPY",
        db,
        period
    )

    if benchmark_df is None or benchmark_df.empty:
        benchmark_growth = None
    else:
        benchmark_returns = benchmark_df[
            "return"
        ].reindex(portfolio_returns.index)

        benchmark_growth = (
            (1 + benchmark_returns).cumprod() * 100
        )

    history = []

    for trading_date in portfolio_growth.index:

        record = {
            "date": trading_date.strftime("%Y-%m-%d"),
            "portfolio": round(
                float(portfolio_growth.loc[trading_date]),
                2
            )
        }

        if (
            benchmark_growth is not None
            and trading_date in benchmark_growth.index
            and not pd.isna(benchmark_growth.loc[trading_date])
        ):
            record["benchmark"] = round(
                float(benchmark_growth.loc[trading_date]),
                2
            )
        else:
            record["benchmark"] = None

        history.append(record)

    return {
        "base_value": 100,
        "benchmark": "SPY",
        "history": history,
        "period": period,
        "data_complete": result["data_complete"]
    }
