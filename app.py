from __future__ import annotations

import os
from typing import Any, Optional

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates

from api.auth import router as auth_router
from api.chat import router as chat_router
from api.clips import router as clips_router
from api.users import router as users_router
from api.websocket import router as websocket_router
from database.db import get_db
from database.schema import create_tables
from services.auth import get_current_user_from_request
from services.chat import get_conversation_by_id, get_other_user, user_in_conversation

app = FastAPI(title="Y")
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(clips_router)
app.include_router(websocket_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup() -> None:
    """Ensure database tables are created before the app starts."""
    create_tables()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[Any]:
    return get_current_user_from_request(request, db)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> Any:
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, user: Any = Depends(get_current_user)) -> Any:
    if not user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request, "home.html", {"request": request, "user": user})


@app.get("/chat/{conversation_id}", response_class=HTMLResponse)
async def chat(
    request: Request,
    conversation_id: int,
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user),
) -> Any:
    if not user:
        return RedirectResponse(url="/", status_code=303)

    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation or not user_in_conversation(conversation, user.id):
        return RedirectResponse(url="/home", status_code=303)

    other_user = get_other_user(db, conversation, user.id)
    return templates.TemplateResponse(
        request,
        "chat.html",
        {
            "request": request,
            "conversation_id": conversation_id,
            "user": user,
            "other_user": other_user,
        },
    )


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, user: Any = Depends(get_current_user)) -> Any:
    if not user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request, "profile.html", {"request": request, "user": user})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
