from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database.db import get_db
from models.user import User
from services.auth import get_current_user_from_request
from services.chat import (
    get_conversation_by_id,
    get_conversations_for_user,
    get_messages_for_conversation,
    get_or_create_conversation,
    user_in_conversation,
)
from services.auth import get_user_by_id

router = APIRouter(tags=["chat"])


def _require_user(request: Request, db: Session) -> User:
    user = get_current_user_from_request(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@router.get("/conversations")
async def list_conversations(request: Request, db: Session = Depends(get_db)) -> Any:
    user = _require_user(request, db)
    return {"conversations": get_conversations_for_user(db, user.id)}


@router.get("/conversations/open/{other_user_id}")
async def open_conversation(
    request: Request,
    other_user_id: int,
    db: Session = Depends(get_db),
) -> Any:
    user = _require_user(request, db)
    if other_user_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot open a conversation with yourself")
    if not get_user_by_id(db, other_user_id):
        raise HTTPException(status_code=404, detail="User not found")

    conversation = get_or_create_conversation(db, user.id, other_user_id)
    return RedirectResponse(url=f"/chat/{conversation.id}", status_code=303)


@router.get("/messages/{conversation_id}")
async def list_messages(
    request: Request,
    conversation_id: int,
    db: Session = Depends(get_db),
) -> Any:
    user = _require_user(request, db)
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation or not user_in_conversation(conversation, user.id):
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"messages": get_messages_for_conversation(db, conversation_id, user.id)}
