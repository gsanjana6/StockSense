from datetime import datetime
from pydantic import BaseModel, ConfigDict



class PortfolioCreate(BaseModel):
    portfolio_name: str

class PortfolioUpdate(BaseModel):
    portfolio_name: str

class PortfolioResponse(BaseModel):
    portfolio_id: int
    portfolio_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)