
import logging
from app.services.llm.llm_response_service import generate_chat_response
from app.services.llm.response_verification_service import (
    verify_llm_response,
)
from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.company import CompanyMeta
from app.models.chat_history import ChatHistory

from app.schemas.chat import ChatResponse

from app.services.intent_extraction_service import extract_intent
from app.services.company_resolution_service import resolve_explicit_ticker

from app.services.parameter_validation_service import (
    validate_portfolio_access,
)

from app.services.portfolio_service import calculate_portfolio_value

from app.services.analytics_service import (
    get_stock_returns,
    get_portfolio_returns,
    calculate_performance_metrics,
    calculate_portfolio_beta,
    calculate_diversification_metrics,
    calculate_correlation_matrix,
)

from app.services.market_data_service import get_current_price
from app.services.technical_analysis import calculate_technical_analysis

from app.services.recommendation_service import (
    generate_portfolio_recommendations
)

from app.services.interpretation_service import (
    generate_portfolio_interpretation
)

from app.services.analytics_service import calculate_health_score
from app.schemas.advanced_simulation import (
    AdvancedWhatIfRequest,
    ScenarioChange,
)

from app.services.advanced_simulation_service import (
    run_advanced_simulation,
)

import re

logger = logging.getLogger(__name__)


# --------------------------------------------------
# PORTFOLIO RESOLUTION
# --------------------------------------------------

def resolve_user_portfolio(
    user_id: int,
    portfolio_id: int | None,
    db: Session
):
    if portfolio_id is not None:
        return validate_portfolio_access(
            portfolio_id,
            user_id,
            db
        )

    portfolios = db.query(Portfolio).filter(
        Portfolio.user_id == user_id
    ).all()

    if len(portfolios) == 1:
        return portfolios[0]

    if len(portfolios) == 0:
        return None

    return "ambiguous"


# --------------------------------------------------
# HISTORY
# --------------------------------------------------

def save_chat_history(
    user_id: int,
    query: str,
    intent: str,
    response: str,
    response_method: str = "deterministic_template",
    validation_status: str = "not_applicable",
    structured_report: dict = None,
    db: Session = None
):
    history = ChatHistory(
        user_id=user_id,
        query=query,
        intent=intent,
        response=response,
        structured_report=structured_report,
        response_method=response_method,
        validation_status=validation_status
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return history


# --------------------------------------------------
# RESPONSE HELPERS
# --------------------------------------------------

def format_currency(value):
    return f"${value:,.2f}"


def format_percentage(value):
    return f"{value:.2f}%"


def get_company(ticker: str, db: Session):
    return db.query(CompanyMeta).filter(
        CompanyMeta.ticker == ticker.upper()
    ).first()


def clarification_response(message: str):
    return message


# --------------------------------------------------
# CHAT ORCHESTRATION
# --------------------------------------------------

def process_chat_message(
    message: str,
    user_id: int,
    db: Session,
    portfolio_id: int | None = None
):
    # 1. Extract intent and parameters.
    intent_result = extract_intent(
        message=message,
        portfolio_id=portfolio_id,
        db=db
    )

    intent = intent_result.intent
    period = intent_result.period or "1y"

    response = None
    llm_context = {}
    
    # 2. Handle unsupported requests.
    if intent == "unsupported":
        response = (
            "I can help with portfolio analytics, stock information, "
            "historical performance, technical indicators and "
            "what-if portfolio simulations. I cannot provide "
            "buy/sell recommendations, predict future prices or "
            "execute trades."
        )

    # 3. Handle clarification.
    elif intent == "clarification":
        response = (
            "I need a little more information to answer accurately. "
            "Please specify the company, stock ticker or portfolio "
            "you want me to analyse."
        )

    # 4. Financial concept.
    elif intent == "financial_concept":
        response = None

    # 5. Stock price.
    elif intent == "stock_price":
        ticker = intent_result.ticker

        if not ticker:
            response = "Which stock's price would you like to check?"
        else:
            company = get_company(ticker, db)
            price = get_current_price(ticker, db)

            if price is None:
                response = (
                    f"I couldn't retrieve a recent closing price "
                    f"for {ticker}."
                )
            else:
                company_name = (
                    company.company_name if company else ticker
                )

                llm_context = {
                    "stock_price": {
                        "ticker": ticker,
                        "company_name": company_name,
                        "latest_available_close": price,
                        "data_source": "StockSense market data service",
                        "price_type": "Latest available daily closing price"
                    }
                }

                response = (
                    f"{company_name} ({ticker}) has a latest "
                    f"available closing price of "
                    f"{format_currency(price)}. "
                    "This is the latest available daily closing "
                    "price, not necessarily a live intraday quote."
                )

    # 6. Company information.
    elif intent == "company_information":
        ticker = intent_result.ticker

        if not ticker:
            response = "Which company would you like to know about?"
        else:
            company = get_company(ticker, db)

            if company is None:
                response = (
                    f"I couldn't retrieve company information "
                    f"for {ticker}."
                )
            else:

                llm_context = {
                    "company_information": {
                        "company_name": company.company_name,
                        "ticker": company.ticker,
                        "sector": company.sector,
                        "country": company.country,
                        "market_cap": (
                            float(company.market_cap)
                            if company.market_cap is not None
                            else None
                        ),
                        "description": company.description
                    }
                }

                response = (
                    f"Company: {company.company_name}\n"
                    f"Ticker: {company.ticker}\n"
                    f"Sector: {company.sector or 'Not available'}\n"
                    f"Country: {company.country or 'Not available'}\n"
                    f"Market capitalisation: "
                    f"{format_currency(company.market_cap) if company.market_cap else 'Not available'}\n"
                    f"Description: "
                    f"{company.description or 'Not available'}"
                )

    # 7. Stock comparison.
    elif intent == "stock_comparison":
        tickers = intent_result.tickers

        if len(tickers) < 2:
            response = (
                "Please specify at least two stocks to compare."
            )
        else:
            results = []
            comparison_data = []

            for ticker in tickers:
                company = get_company(ticker, db)
                price = get_current_price(ticker, db)

                stock_returns = get_stock_returns(
                    ticker,
                    db,
                    period
                )

                if price is None or stock_returns is None:
                    results.append(
                        f"{ticker}: Insufficient market data."
                    )
                    continue

                total_return = (
                    (1 + stock_returns["return"]).prod() - 1
                ) * 100
                
                comparison_data.append({
                    "ticker": ticker,
                    "company_name": (
                        company.company_name if company else ticker
                    ),
                    "latest_available_close": price,
                    "historical_return_pct": round(
                        float(total_return), 2
                    ),
                    "period": period
                })

                name = (
                    company.company_name if company else ticker
                )

                results.append(
                    f"{name} ({ticker})\n"
                    f"Latest available close: {format_currency(price)}\n"
                    f"Historical return over {period}: "
                    f"{format_percentage(total_return)}"
                )
            if comparison_data:
                llm_context = {
                    "stock_comparison": {
                        "period": period,
                        "stocks": comparison_data,
                        "data_source": "StockSense market data service"
                    }
                }

            response = (
                f"Stock comparison over {period}:\n\n"
                + "\n\n".join(results)
                + "\n\nHistorical performance does not predict "
                "future returns."
            )

    # 8. Technical analysis.
    elif intent == "technical_analysis":
        ticker = intent_result.ticker

        if not ticker:
            response = (
                "Which stock would you like me to analyse technically?"
            )
        else:
            try:
                result = calculate_technical_analysis(ticker)
                llm_context = {
                    "technical_analysis": result
                }
                indicators = result["indicators"]
                interpretation = result["interpretation"]

                response = (
                    f"Technical analysis: {ticker}\n"
                    f"Data date: {result['data_date']}\n"
                    f"Closing price: "
                    f"{format_currency(result['current_price'])}\n\n"
                    f"SMA 20: {indicators['sma_20']}\n"
                    f"SMA 50: {indicators['sma_50']}\n"
                    f"SMA 200: {indicators['sma_200']}\n"
                    f"RSI 14: {indicators['rsi_14']}\n"
                    f"MACD: {indicators['macd']}\n\n"
                    f"Trend: {interpretation['long_term_trend']}\n"
                    f"Moving averages: "
                    f"{interpretation['moving_average_alignment']}\n"
                    f"RSI: {interpretation['rsi']}\n"
                    f"MACD: {interpretation['macd']}\n"
                    f"Volatility: {interpretation['volatility']}\n\n"
                    f"{result['disclaimer']}"
                )

            except Exception:
                logger.exception(
                    "Technical analysis failed for %s",
                    ticker
                )
                response = (
                    f"Technical analysis is currently unavailable "
                    f"for {ticker}."
                )

    # 9. Portfolio-related intents.
    elif intent in {
        "portfolio_summary",
        "performance_metrics",
        "benchmark_comparison",
        "diversification",
        "correlation",
        "portfolio_health",
        "what_if",
    }:

        portfolio = resolve_user_portfolio(
            user_id,
            intent_result.portfolio_id,
            db
        )

        if portfolio is None:
            response = (
                "You don't have a portfolio registered yet. "
                "Create a portfolio before requesting portfolio analysis."
            )

        elif portfolio == "ambiguous":
            response = (
                "You have multiple portfolios. Please specify "
                "the portfolio ID you want me to analyse."
            )

        else:
            pid = portfolio.portfolio_id

            # Portfolio summary.
            if intent == "portfolio_summary":
                valuation = calculate_portfolio_value(pid, db)

                actual_holdings = db.query(Holding).filter(
                    Holding.portfolio_id == pid
                ).count()

                available_holdings = len(
                    valuation.get("holdings", [])
                )

                if available_holdings != actual_holdings:
                    response = (
                        "I couldn't retrieve market prices for every "
                        "holding. The portfolio summary is incomplete, "
                        "so I won't present partial figures as the "
                        "complete portfolio value."
                    )
                else:
                    llm_context = {
                        "portfolio_summary": {
                            "portfolio_name": portfolio.portfolio_name,
                            "total_invested": valuation["total_invested"],
                            "current_value": valuation["current_value"],
                            "total_gain_loss": valuation["total_gain_loss"],
                            "return_percentage": valuation["return_percentage"],
                            "holdings": valuation["holdings"]
                        }
                    }

                    holdings_text = "\n".join(
                        f"- {holding['ticker']}: "
                        f"{holding['quantity']} units, "
                        f"value {format_currency(holding['current_value'])}"
                        for holding in valuation["holdings"]
                    )

                    response = (
                        f"Portfolio: {portfolio.portfolio_name}\n"
                        f"Total invested: "
                        f"{format_currency(valuation['total_invested'])}\n"
                        f"Current value: "
                        f"{format_currency(valuation['current_value'])}\n"
                        f"Gain/loss: "
                        f"{format_currency(valuation['total_gain_loss'])}\n"
                        f"Return: "
                        f"{format_percentage(valuation['return_percentage'])}\n\n"
                        f"Holdings:\n{holdings_text}"
                    )

            # Performance metrics.
            elif intent == "performance_metrics":
                metrics = calculate_performance_metrics(
                    pid,
                    db,
                    period
                )

                if metrics is None:
                    response = (
                        "I couldn't calculate complete portfolio "
                        "performance. Check whether market history "
                        "is available for all holdings."
                    )
                else:
                    llm_context = {
                        "performance_metrics": {
                            "period": period,
                            "metrics": metrics
                        }
                    }

                    response = (
                        f"Portfolio performance ({period}):\n"
                        f"Annualised return: "
                        f"{format_percentage(metrics['annualized_return'])}\n"
                        f"Annualised volatility: "
                        f"{format_percentage(metrics['annualized_volatility'])}\n"
                        f"Sharpe ratio: {metrics['sharpe_ratio']}\n"
                        f"Maximum drawdown: "
                        f"{format_percentage(metrics['max_drawdown'])}\n"
                        f"Observations: {metrics['observations']}"
                    )

            # Benchmark comparison.
            elif intent == "benchmark_comparison":
                portfolio_result = get_portfolio_returns(
                    pid,
                    db,
                    period
                )

                benchmark = intent_result.benchmark or "SPY"

                benchmark_returns = get_stock_returns(
                    benchmark,
                    db,
                    period
                )

                if (
                    portfolio_result is None
                    or benchmark_returns is None
                ):
                    response = (
                        "I couldn't retrieve sufficient data "
                        "to compare your portfolio with the benchmark."
                    )
                else:
                    portfolio_returns = (
                        portfolio_result["returns"]["portfolio_return"]
                    )

                    aligned = portfolio_returns.align(
                        benchmark_returns["return"],
                        join="inner"
                    )

                    portfolio_total = (
                        (1 + aligned[0]).prod() - 1
                    ) * 100

                    benchmark_total = (
                        (1 + aligned[1]).prod() - 1
                    ) * 100
                    
                    llm_context = {
                        "benchmark_comparison": {
                            "benchmark": benchmark,
                            "period": period,
                            "portfolio_return_pct": round(
                                float(portfolio_total), 2
                            ),
                            "benchmark_return_pct": round(
                                float(benchmark_total), 2
                            ),
                            "difference_percentage_points": round(
                                float(portfolio_total - benchmark_total), 2
                            )
                        }
                    }

                    response = (
                        f"Portfolio vs {benchmark} ({period}):\n"
                        f"Portfolio historical return: "
                        f"{format_percentage(portfolio_total)}\n"
                        f"{benchmark} historical return: "
                        f"{format_percentage(benchmark_total)}\n"
                        f"Difference: "
                        f"{format_percentage(portfolio_total - benchmark_total)}"
                    )

            # Diversification.
            elif intent == "diversification":
                metrics = calculate_diversification_metrics(
                    pid,
                    db,
                    period
                )

                if metrics is None:
                    response = (
                        "I couldn't calculate diversification metrics "
                        "because complete portfolio data is unavailable."
                    )
                else:
                    weights_text = "\n".join(
                        f"- {ticker}: {weight:.2f}%"
                        for ticker, weight in metrics["weights"].items()
                    )
                    llm_context = {
                        "diversification": {
                            "period": period,
                            "metrics": metrics
                        }
                    }
                    response = (
                        f"Portfolio diversification:\n"
                        f"Concentration index: "
                        f"{metrics['concentration_index']}\n"
                        f"Effective holdings: "
                        f"{metrics['effective_holdings']}\n"
                        f"Largest holding: "
                        f"{metrics['largest_holding']} "
                        f"({metrics['largest_weight']}%)\n\n"
                        f"Portfolio weights:\n{weights_text}"
                    )

            # Correlation.
            elif intent == "correlation":
                matrix = calculate_correlation_matrix(
                    pid,
                    db,
                    period
                )

                if matrix is None:
                    response = (
                        "I couldn't calculate the correlation matrix "
                        "with the available portfolio data."
                    )
                else:
                    llm_context = {
                        "correlation": {
                            "period": period,
                            "matrix": matrix.round(4).to_dict()
                        }
                    }
                    response = (
                        f"Portfolio correlation matrix ({period}):\n"
                        f"{matrix.round(3).to_string()}\n\n"
                        "Correlation measures how asset returns "
                        "move in relation to one another. It does "
                        "not establish causation."
                    )
            
            
            # Portfolio health assessment.
            elif intent == "portfolio_health":

                health = calculate_health_score(pid, db)

                interpretation = generate_portfolio_interpretation(
                    pid, db
                )

                recommendations = generate_portfolio_recommendations(
                    pid, db
                )

                if (
                    health is None
                    or interpretation is None
                    or recommendations.get("status") != "success"
                ):
                    llm_context = {
                        "portfolio_health": {
                            "status": "unavailable",
                            "reason": "Insufficient market data"
                        }
                    }

                else:
                    llm_context = {
                        "portfolio_health": {
                            "status": "success",
                            "health_score": health,
                            "interpretation": interpretation,
                            "recommendations": recommendations
                        }
                    }

                    recommendation_items = recommendations.get(
                        "recommendations", []
                    )

                    if isinstance(recommendation_items, list):
                        recommendations_text = "\n".join(
                            f"- {item}"
                            if isinstance(item, str)
                            else f"- {item.get('title', item.get('description', str(item)))}"
                            if isinstance(item, dict)
                            else f"- {item}"
                            for item in recommendation_items
                        )
                    else:
                        recommendations_text = str(recommendation_items)

                    response = (
                        f"Portfolio Health Assessment\n"
                        f"Health score: {health.get('health_score', 'N/A')}/100 "
                        f"({health.get('rating', 'N/A')})\n\n"
                        f"Interpretation:\n{interpretation}\n\n"
                        f"Recommendations:\n{recommendations_text}"
                    )
            # What-if portfolio simulation.
            elif intent == "what_if":

                ticker = intent_result.ticker

                if not ticker:
                    response = (
                        "Which stock would you like to add, "
                        "reduce or remove in the simulation?"
                    )

                else:
                    text_lower = message.lower()

                    if any(
                        phrase in text_lower
                        for phrase in ["remove", "delete"]
                    ):
                        action = "remove"

                    elif any(
                        phrase in text_lower
                        for phrase in ["reduce", "decrease"]
                    ):
                        action = "reduce"

                    elif any(
                        phrase in text_lower
                        for phrase in ["add", "increase"]
                    ):
                        action = "add"

                    else:
                        action = None

                    # Extract dollar amounts.
                    dollar_match = re.search(
                        r"\$\s*([\d,]+(?:\.\d{1,2})?)"
                        r"|([\d,]+(?:\.\d{1,2})?)\s*(?:dollars?|usd)\b",
                        text_lower
                    )

                    # Extract share quantities.
                    shares_match = re.search(
                        r"\b([\d,]+(?:\.\d{1,2})?)\s*(?:shares?|units?)\b",
                        text_lower
                    )

                    amount = None
                    amount_type = "dollars"

                    if shares_match:
                        amount = float(
                            shares_match.group(1).replace(",", "")
                        )
                        amount_type = "shares"

                    elif dollar_match:
                        amount_text = (
                            dollar_match.group(1)
                            or dollar_match.group(2)
                        )

                        amount = float(
                            amount_text.replace(",", "")
                        )
                        amount_type = "dollars"

                    if action is None:
                        response = (
                            "Would you like to add, reduce or "
                            "remove this stock in the simulation?"
                        )

                    elif action != "remove" and amount is None:
                        response = (
                            "Please specify either a dollar amount "
                            "or a share quantity for this hypothetical change."
                        )

                    else:
                        try:
                            request = AdvancedWhatIfRequest(
                                changes=[
                                    ScenarioChange(
                                        ticker=ticker,
                                        action=action,
                                        amount=amount,
                                        amount_type=amount_type
                                    )
                                ],
                                benchmark="SPY",
                                period=(
                                    period
                                    if period in {"1y", "2y", "5y"}
                                    else "1y"
                                )
                            )
                            logger.warning(
                                "WHAT-IF REQUEST: %s",
                                request.model_dump()
                            )
                            simulation = run_advanced_simulation(
                                pid,
                                request,
                                db
                            )

                            if "error" in simulation:
                                response = (
                                    "The simulation could not be "
                                    "completed: "
                                    + simulation["error"]
                                )

                            else:
                                current = simulation["current"]
                                simulated = simulation["simulated"]
                                comparison = simulation["comparison"]

                                if action == "remove":
                                    change_description = f"Remove {ticker}"
                                else:
                                    unit_label = (
                                        "shares"
                                        if amount_type == "shares"
                                        else "dollars"
                                    )

                                    amount_display = (
                                        f"{amount:g} {unit_label}"
                                        if amount_type == "shares"
                                        else format_currency(amount)
                                    )

                                    change_description = (
                                        f"{action.title()} {amount_display} of {ticker}"
                                    )

                                response = (
                                    "WHAT-IF PORTFOLIO SIMULATION\n\n"

                                    f"Hypothetical change: {change_description}\n\n"

                                    "CURRENT PORTFOLIO\n"
                                    f"Total value: "
                                    f"{format_currency(current['total_value'])}\n"
                                    f"Annualised return: "
                                    f"{format_percentage(current['annualized_return'])}\n"
                                    f"Annualised volatility: "
                                    f"{format_percentage(current['annualized_volatility'])}\n"
                                    f"Sharpe ratio: {current['sharpe_ratio']}\n\n"

                                    "SIMULATED PORTFOLIO\n"
                                    f"Total value: "
                                    f"{format_currency(simulated['total_value'])}\n"
                                    f"Annualised return: "
                                    f"{format_percentage(simulated['annualized_return'])}\n"
                                    f"Annualised volatility: "
                                    f"{format_percentage(simulated['annualized_volatility'])}\n"
                                    f"Sharpe ratio: {simulated['sharpe_ratio']}\n\n"

                                    "CHANGE IN METRICS\n"
                                    f"Portfolio value change: "
                                    f"{format_currency(comparison['investment_value_change'])}\n"
                                    f"Annualised return change: "
                                    f"{format_percentage(comparison['return_change'])}\n"
                                    f"Volatility change: "
                                    f"{format_percentage(comparison['volatility_change'])}\n"
                                    f"Sharpe ratio change: "
                                    f"{comparison['sharpe_change']}\n"
                                )

                                if comparison["beta_change"] is not None:
                                    response += (
                                        f"Beta change: "
                                        f"{comparison['beta_change']}\n"
                                    )

                                response += (
                                    "\nThis is a hypothetical simulation based on "
                                    "available historical market data. It does not "
                                    "represent a prediction of future performance."
                                )

                        except Exception:
                            logger.exception(
                                "What-if simulation failed"
                            )

                            response = (
                                "The portfolio simulation is "
                                "currently unavailable."
                            )

    # 11. Generate and verify the natural-language response.

    data_required_intents = {
        "stock_price",
        "company_information",
        "stock_comparison",
        "technical_analysis",
        "portfolio_summary",
        "performance_metrics",
        "benchmark_comparison",
        "diversification",
        "correlation",
        "portfolio_health",
        "what_if",
    }

    if intent in {"unsupported", "clarification"}:
        response_method = "deterministic_template"
        validation_status = "not_applicable"

    elif (
        intent in data_required_intents
        and not llm_context
    ):
        if not isinstance(response, str) or not response:
            response = (
                "I couldn't retrieve sufficient verified data "
                "to answer that request accurately."
            )

        response_method = "deterministic_template"
        validation_status = "not_applicable"

    else:
        llm_result = generate_chat_response(
            message=message,
            context=llm_context
        )

        if llm_result["success"]:

            generated_response = llm_result["response"]
            logger.warning(
                "LLM GENERATED RESPONSE FOR VERIFICATION: %s",
                generated_response
            )
            # Verify financial-data answers against backend data.
            if intent in data_required_intents:

                verification = verify_llm_response(
                    response=generated_response,
                    context=llm_context
                )
                logger.warning(
                    "LLM VERIFICATION DEBUG: %s",
                    verification
                )
                validation_status = verification["status"]

                if validation_status == "passed":
                    response = generated_response
                    response_method = (
                        llm_result["model"] or "gemma"
                    )

                else:
                    logger.warning(
                        "LLM response verification failed: %s",
                        verification
                    )

                    response = (
                        "I couldn't verify all the financial figures "
                        "in the generated explanation against the "
                        "available StockSense data. Please try again."
                    )

                    response_method = "deterministic_template"

            else:
                # Conceptual answers do not require market-data verification.
                response = generated_response
                response_method = llm_result["model"] or "gemma"
                validation_status = "not_applicable"

        else:
            logger.warning(
                "LLM generation failed: %s",
                llm_result.get("error")
            )

            if not isinstance(response, str) or not response:
                response = (
                    "The AI explanation service is currently "
                    "unavailable. Please try again."
                )

            response_method = "deterministic_template"
            validation_status = "not_applicable"
  
    # 12. Persist the conversation.
    history = save_chat_history(
        user_id=user_id,
        query=message,
        intent=intent,
        response=response,
        response_method=response_method,
        validation_status=validation_status,
        structured_report=llm_context,
        db=db
    )

    return ChatResponse(
        chat_id=history.chat_id,
        intent=intent,
        response=response,
        response_method=(
            "gemini"
            if response_method.startswith("gemini")
            else "gemma"
            if response_method.startswith("gemma")
            else "deterministic_template"
        ),
        validation_status=validation_status
    )
