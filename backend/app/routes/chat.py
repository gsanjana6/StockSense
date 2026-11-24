
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.models.chat_history import ChatHistory
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatHistoryItem,
)
from app.services.chat_service import process_chat_message
from app.utils.auth import get_current_user

router = APIRouter(
    prefix="/chat",
    tags=["Chatbot"]
)


# --------------------------------------------------
# SEND MESSAGE
# --------------------------------------------------

@router.post("/", response_model=ChatResponse)
def send_chat_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return process_chat_message(
            message=request.message,
            user_id=current_user.user_id,
            db=db,
            portfolio_id=request.portfolio_id
        )

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your message."
        )


# --------------------------------------------------
# GET CHAT HISTORY
# --------------------------------------------------

@router.get("/history", response_model=list[ChatHistoryItem])
def get_chat_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    records = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == current_user.user_id)
        .order_by(ChatHistory.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        ChatHistoryItem(
            chat_id=record.chat_id,
            query=record.query,
            intent=record.intent,
            response=record.response,
            created_at=record.created_at.isoformat()
        )
        for record in records
    ]


# --------------------------------------------------
# GET A SPECIFIC CHAT MESSAGE
# --------------------------------------------------

@router.get("/history/{chat_id}", response_model=ChatHistoryItem)
def get_chat_history_item(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = (
        db.query(ChatHistory)
        .filter(
            ChatHistory.chat_id == chat_id,
            ChatHistory.user_id == current_user.user_id
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Chat history entry not found."
        )

    return ChatHistoryItem(
        chat_id=record.chat_id,
        query=record.query,
        intent=record.intent,
        response=record.response,
        created_at=record.created_at.isoformat()
    )
