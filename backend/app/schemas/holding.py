from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


from pydantic import BaseModel, Field


class HoldingCreate(BaseModel):
    ticker: str
    quantity: float = Field(gt=0)
    avg_buy_price: float = Field(gt=0)


from typing import Optional
from pydantic import BaseModel, Field


class HoldingUpdate(BaseModel):
    quantity: Optional[float] = Field(
        default=None,
        gt=0
    )

    avg_buy_price: Optional[float] = Field(
        default=None,
        gt=0
    )


class HoldingResponse(BaseModel):
    holding_id: int
    portfolio_id: int
    ticker: str
    quantity: Decimal
    avg_buy_price: Decimal
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)