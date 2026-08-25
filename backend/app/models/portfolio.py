from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, text
from app.database.base import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    portfolio_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    portfolio_name = Column(
        String(100),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )