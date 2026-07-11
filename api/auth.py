from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database.db import get_db
from services.auth import authenticate_user, create_user, get_user_by_username

router = APIRouter()


def redirect_home() -> RedirectResponse:
    return RedirectResponse(url="/home", status_code=303)


def redirect_index() -> RedirectResponse:
    return RedirectResponse(url="/", status_code=303)


@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    display_name: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> Any:
    if get_user_by_username(db, username.strip()):
        raise HTTPException(status_code=409, detail="Username is already taken")

    try:
        user = create_user(db, username=username, display_name=display_name, password=password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    request.session["user_id"] = user.id
    return redirect_home()


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> Any:
    user = authenticate_user(db, username=username, password=password)
    if not user:
        return redirect_index()

    request.session["user_id"] = user.id
    return redirect_home()


@router.get("/logout")
async def logout(request: Request) -> Any:
    request.session.pop("user_id", None)
    return redirect_index()
