from sqlalchemy import Column, Integer, String, Date, DECIMAL, BigInteger

from app.database.base import Base


class PriceCache(Base):
    __tablename__ = "price_cache"

    price_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    ticker = Column(
        String(15),
        nullable=False,
        index=True
    )

    price_date = Column(
        Date,
        nullable=False
    )

    open = Column(
        DECIMAL(12, 2),
        nullable=True
    )

    high = Column(
        DECIMAL(12, 2),
        nullable=True
    )

    low = Column(
        DECIMAL(12, 2),
        nullable=True
    )

    close = Column(
        DECIMAL(12, 2),
        nullable=True
    )

    volume = Column(
        BigInteger,
        nullable=True
    )