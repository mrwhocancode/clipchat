from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.db import get_db
from models.user import User
from services.auth import get_current_user_from_request
from services.chat import get_conversation_by_id, get_other_user_id, user_in_conversation
from services.clips import list_available_clips, search_available_clips, send_clip
from services.websocket import manager

router = APIRouter(tags=["clips"])


class SendClipRequest(BaseModel):
    receiver_id: int = Field(..., gt=0)
    clip_id: str = Field(..., min_length=1, max_length=128)


def _require_user(request: Request, db: Session) -> User:
    user = get_current_user_from_request(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@router.get("/clips")
async def get_clips(request: Request, db: Session = Depends(get_db)) -> Any:
    _require_user(request, db)
    return {"clips": list_available_clips()}


@router.get("/clips/search")
async def search_clips(
    request: Request,
    q: str = Query(..., min_length=1, max_length=100),
    db: Session = Depends(get_db),
) -> Any:
    _require_user(request, db)
    return {"clips": search_available_clips(q)}


@router.post("/send")
async def send_clip_message(
    request: Request,
    body: SendClipRequest,
    db: Session = Depends(get_db),
) -> Any:
    user = _require_user(request, db)

    try:
        message = send_clip(db, user.id, body.receiver_id, body.clip_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    conversation = get_conversation_by_id(db, message["conversation_id"])
    if conversation:
        receiver_id = get_other_user_id(conversation, user.id)
        if receiver_id:
            await manager.broadcast_new_message(receiver_id, message)

    return {"message": message}
