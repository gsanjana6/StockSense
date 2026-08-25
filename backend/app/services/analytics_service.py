import pandas as pd

from sqlalchemy.orm import Session

from app.models.holding import Holding
from app.models.price_cache import PriceCache
from app.services.market_data_service import cache_historical_prices


def get_stock_returns(
    ticker: str,
    db: Session,
    period: str = "1y"
):
    ticker = ticker.upper()

    # Make sure historical prices are available in the cache
    cache_historical_prices(
        ticker=ticker,
        db=db,
        period=period
    )

    # Retrieve cached closing prices
    prices = (
        db.query(PriceCache)
        .filter(PriceCache.ticker == ticker)
        .order_by(PriceCache.price_date.asc())
        .all()
    )

    if len(prices) < 2:
        return None

    # Convert database records to a pandas DataFrame
    df = pd.DataFrame([
        {
            "date": price.price_date,
            "close": float(price.close)
        }
        for price in prices
    ])

    df.set_index("date", inplace=True)

    # Calculate daily percentage returns
    df["return"] = df["close"].pct_change()

    # First observation has no previous day for comparison
    df.dropna(inplace=True)

    return df

def get_portfolio_returns(
    portfolio_id: int,
    db: Session
):
    # Get portfolio holdings
    holdings = db.query(Holding).filter(
        Holding.portfolio_id == portfolio_id
    ).all()

    if not holdings:
        return None

    returns_data = {}
    holding_values = {}

    # Get returns and current value for each holding
    for holding in holdings:
        ticker = holding.ticker.upper()

        stock_returns = get_stock_returns(
            ticker,
            db
        )

        if stock_returns is None:
            continue

        # Use latest cached closing price
        latest_price = (
            db.query(PriceCache)
            .filter(PriceCache.ticker == ticker)
            .order_by(PriceCache.price_date.desc())
            .first()
        )

        if latest_price is None:
            continue

        current_value = (
            float(holding.quantity)
            * float(latest_price.close)
        )

        holding_values[ticker] = current_value
        returns_data[ticker] = stock_returns["return"]

    if not returns_data:
        return None

    # Align all stocks by trading date
    returns_df = pd.DataFrame(returns_data).dropna()

    total_value = sum(holding_values.values())

    if total_value == 0:
        return None

    # Calculate portfolio weights
    weights = {
        ticker: value / total_value
        for ticker, value in holding_values.items()
    }

    # Weighted portfolio daily return
    returns_df["portfolio_return"] = sum(
        returns_df[ticker] * weights[ticker]
        for ticker in returns_df.columns
    )

    return {
        "returns": returns_df,
        "weights": weights
    }

def calculate_performance_metrics(
    portfolio_id: int,
    db: Session
):
    result = get_portfolio_returns(
        portfolio_id,
        db
    )

    if result is None:
        return None

    portfolio_returns = result["returns"]["portfolio_return"]

    if portfolio_returns.empty:
        return None

    trading_days = 252

    # Annualized return using compounded daily returns
    cumulative_growth = (
        1 + portfolio_returns
    ).prod()

    number_of_days = len(portfolio_returns)

    annualized_return = (
        cumulative_growth ** (
            trading_days / number_of_days
        )
    ) - 1

    # Annualized volatility
    annualized_volatility = (
        portfolio_returns.std()
        * (trading_days ** 0.5)
    )
    # Risk-free rate assumption: 4% annually
    risk_free_rate = 0.04

    # Sharpe Ratio
    sharpe_ratio = (
        (annualized_return - risk_free_rate)
        / annualized_volatility
        if annualized_volatility > 0
        else 0
    )

    # Cumulative portfolio growth
    cumulative_returns = (
        1 + portfolio_returns
    ).cumprod()

    # Running portfolio peak
    running_peak = cumulative_returns.cummax()

    # Drawdown from previous peak
    drawdown = (
        cumulative_returns / running_peak
    ) - 1

    # Maximum Drawdown
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
        "observations": number_of_days
    }

def calculate_portfolio_beta(
    portfolio_id: int,
    db: Session,
    benchmark: str = "SPY"
):
    # Get portfolio returns
    portfolio_result = get_portfolio_returns(
        portfolio_id,
        db
    )

    if portfolio_result is None:
        return None

    portfolio_returns = (
        portfolio_result["returns"]["portfolio_return"]
    )

    # Get benchmark returns
    benchmark_returns_df = get_stock_returns(
        benchmark,
        db
    )

    if benchmark_returns_df is None:
        return None

    benchmark_returns = benchmark_returns_df["return"]

    # Align portfolio and benchmark returns by date
    combined = pd.concat(
        [
            portfolio_returns.rename("portfolio"),
            benchmark_returns.rename("benchmark")
        ],
        axis=1
    ).dropna()

    if len(combined) < 2:
        return None

    # Calculate covariance
    covariance = combined["portfolio"].cov(
        combined["benchmark"]
    )

    # Calculate benchmark variance
    market_variance = combined["benchmark"].var()

    if market_variance == 0:
        return None

    # Portfolio beta
    beta = covariance / market_variance

    return round(float(beta), 2)

def calculate_correlation_matrix(
    portfolio_id: int,
    db: Session
):
    result = get_portfolio_returns(
        portfolio_id,
        db
    )

    if result is None:
        return None

    returns_df = result["returns"].copy()

    # Remove the combined portfolio return column
    stock_returns = returns_df.drop(
        columns=["portfolio_return"],
        errors="ignore"
    )

    if stock_returns.empty:
        return None

    # Calculate correlation between holdings
    correlation_matrix = stock_returns.corr()

    return correlation_matrix

def calculate_diversification_metrics(
    portfolio_id: int,
    db: Session
):
    result = get_portfolio_returns(
        portfolio_id,
        db
    )

    if result is None:
        return None

    weights = result["weights"]

    if not weights:
        return None

    # Herfindahl-Hirschman Index (HHI)
    concentration_index = sum(
        weight ** 2
        for weight in weights.values()
    )

    # Effective number of equally weighted holdings
    effective_holdings = (
        1 / concentration_index
        if concentration_index > 0
        else 0
    )

    # Largest position in the portfolio
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
        }
    }

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

    concentration = diversification[
        "concentration_index"
    ]

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

    # -------------------------
    # 3. Beta Score (0–25)
    # -------------------------

    if 0.8 <= beta <= 1.2:
        beta_score = 25
    elif 0.6 <= beta < 0.8 or 1.2 < beta <= 1.4:
        beta_score = 20
    elif 0.4 <= beta < 0.6 or 1.4 < beta <= 1.6:
        beta_score = 15
    else:
        beta_score = 10

    # -------------------------
    # 4. Concentration Score
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

def get_portfolio_performance_history(
    portfolio_id: int,
    db: Session
):
    result = get_portfolio_returns(
        portfolio_id,
        db
    )

    if result is None:
        return None

    returns_df = result["returns"].copy()

    if returns_df.empty:
        return None

    portfolio_returns = returns_df[
        "portfolio_return"
    ].dropna()

    # Start portfolio growth at 100
    portfolio_growth = (
        (1 + portfolio_returns).cumprod() * 100
    )

    # Get SPY benchmark returns
    benchmark_df = get_stock_returns(
        "SPY",
        db
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

    for date in portfolio_growth.index:

        record = {
            "date": date.strftime("%Y-%m-%d"),
            "portfolio": round(
                float(portfolio_growth.loc[date]),
                2
            )
        }

        if (
            benchmark_growth is not None
            and date in benchmark_growth.index
            and not pd.isna(benchmark_growth.loc[date])
        ):
            record["benchmark"] = round(
                float(benchmark_growth.loc[date]),
                2
            )
        else:
            record["benchmark"] = None

        history.append(record)

    return {
        "base_value": 100,
        "benchmark": "SPY",
        "history": history
    }