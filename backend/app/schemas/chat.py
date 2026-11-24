from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


ChatIntent = Literal[
    "portfolio_summary",
    "performance_metrics",
    "benchmark_comparison",
    "stock_comparison",
    "diversification",
    "correlation",
    "portfolio_health",
    "technical_analysis",
    "stock_price",
    "company_information",
    "what_if",
    "financial_concept",
    "unsupported",
    "clarification"
]

Period = Literal[
    "1mo",
    "3mo",
    "6mo",
    "1y",
    "2y",
    "5y"
]


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=2000)
    portfolio_id: Optional[int] = Field(default=None, gt=0)


class IntentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: ChatIntent
    confidence: float = Field(ge=0, le=1)

    ticker: Optional[str] = None
    period: Optional[Period] = None
    benchmark: Optional[str] = None
    portfolio_id: Optional[int] = Field(default=None, gt=0)
    tickers: list[str] = Field(default_factory=list)
    extraction_source: Literal[
        "rules",
        "gemini",
        "gemma"
    ] = "rules"


class ChatResponse(BaseModel):
    chat_id: Optional[int] = None
    intent: ChatIntent
    response: str
    response_method: Literal[
        "gemini",
        "gemma",
        "deterministic_template"
    ]
    validation_status: Literal[
        "passed",
        "failed",
        "not_applicable"
    ]


class ChatHistoryItem(BaseModel):
    chat_id: int
    query: str
    intent: str
    response: str
    created_at: str