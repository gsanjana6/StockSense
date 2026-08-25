from pydantic import BaseModel, Field
from typing import List


class SimulatedHolding(BaseModel):
    ticker: str
    quantity: float = Field(gt=0)


class WhatIfRequest(BaseModel):
    holdings: List[SimulatedHolding]