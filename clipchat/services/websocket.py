from __future__ import annotations

import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Track active WebSocket connections per authenticated user."""

    def __init__(self) -> None:
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.setdefault(user_id, []).append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        connections = self.active_connections.get(user_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self.active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, payload: dict[str, Any]) -> None:
        connections = list(self.active_connections.get(user_id, []))
        for websocket in connections:
            try:
                await websocket.send_text(json.dumps(payload))
            except Exception:
                self.disconnect(user_id, websocket)

    async def broadcast_new_message(self, receiver_id: int, message: dict[str, Any]) -> None:
        await self.send_to_user(
            receiver_id,
            {
                "type": "new_message",
                "message": message,
            },
        )


manager = ConnectionManager()
