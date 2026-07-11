from __future__ import annotations

from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from database.db import SessionLocal
from services.auth import get_user_by_id
from services.websocket import manager

router = APIRouter(tags=["websocket"])


def _get_user_id_from_websocket(websocket: WebSocket) -> int | None:
    session = websocket.scope.get("session") or {}
    user_id = session.get("user_id")
    return int(user_id) if user_id is not None else None


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> Any:
    user_id = _get_user_id_from_websocket(websocket)
    if not user_id:
        await websocket.close(code=4401)
        return

    db = SessionLocal()
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            await websocket.close(code=4401)
            return

        await manager.connect(user.id, websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            pass
    finally:
        manager.disconnect(user_id, websocket)
        db.close()
