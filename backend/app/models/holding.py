from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func

from app.database.base import Base


class Holding(Base):
    __tablename__ = "holdings"

    holding_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    portfolio_id = Column(
        Integer,
        ForeignKey("portfolios.portfolio_id"),
        nullable=False
    )

    ticker = Column(
        String(15),
        nullable=False
    )

    quantity = Column(
        DECIMAL(12, 4),
        nullable=False
    )

    avg_buy_price = Column(
        DECIMAL(12, 2),
        nullable=False
    )

    added_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )