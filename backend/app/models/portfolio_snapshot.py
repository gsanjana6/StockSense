from sqlalchemy import (
    Column,
    Integer,
    Date,
    DECIMAL,
    ForeignKey
)

from app.database.base import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    snapshot_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    portfolio_id = Column(
        Integer,
        ForeignKey("portfolios.portfolio_id"),
        nullable=False
    )

    snapshot_date = Column(
        Date,
        nullable=False
    )

    total_value = Column(
        DECIMAL(15, 2),
        nullable=True
    )

    daily_return = Column(
        DECIMAL(10, 6),
        nullable=True
    )