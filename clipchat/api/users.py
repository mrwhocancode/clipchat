from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from database.db import get_db
from models.user import User
from services.auth import get_current_user_from_request
from services.search import search_users

router = APIRouter(prefix="/users", tags=["users"])


def _require_user(request: Request, db: Session) -> User:
    user = get_current_user_from_request(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@router.get("/search")
async def search(
    request: Request,
    q: str = Query("", min_length=0),
    db: Session = Depends(get_db),
) -> Any:
    user = _require_user(request, db)
    return {"users": search_users(db, q, int(user.id))}
