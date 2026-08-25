from sqlalchemy import Column, String, BigInteger, Text

from app.database.base import Base


class CompanyMeta(Base):
    __tablename__ = "company_meta"

    ticker = Column(
        String(15),
        primary_key=True
    )

    company_name = Column(
        String(255),
        nullable=False
    )

    sector = Column(
        String(100),
        nullable=True
    )

    country = Column(
        String(100),
        nullable=True
    )

    market_cap = Column(
        BigInteger,
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )