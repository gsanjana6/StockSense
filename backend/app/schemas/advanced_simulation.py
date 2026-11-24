from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ScenarioChange(BaseModel):
    ticker: str
    action: Literal["add", "reduce", "remove"]
    amount: Optional[float] = Field(default=None, gt=0)
    amount_type: Literal["dollars", "shares"] = "dollars"


class AdvancedWhatIfRequest(BaseModel):
    changes: List[ScenarioChange]
    benchmark: str = "SPY"
    period: Literal["1y", "2y", "5y"] = "1y"