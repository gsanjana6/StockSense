
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    TIMESTAMP,
    ForeignKey,
    text,
    Index,
)

from app.database.base import Base
from sqlalchemy import JSON

class ChatHistory(Base):
    __tablename__ = "chat_history"

    chat_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )

    query = Column(
        Text,
        nullable=False
    )

    intent = Column(
        String(50),
        nullable=False
    )

    response = Column(
        Text,
        nullable=False
    )

    response_method = Column(
        String(30),
        nullable=False
    )

    validation_status = Column(
        String(30),
        nullable=False
    )
    
    structured_report = Column(
        JSON,
        nullable=True
    )

    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        Index("ix_chat_history_user_created", "user_id", "created_at"),
    )
