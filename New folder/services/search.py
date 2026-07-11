from __future__ import annotations

from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.user import User


def search_users(db: Session, query: str, current_user_id: int, limit: int = 20) -> list[dict[str, Any]]:
    """Search users by username or display_name, excluding the current user."""
    if not query.strip():
        return []

    pattern = f"%{query.strip()}%"
    users = (
        db.query(User)
        .filter(User.id != current_user_id)
        .filter(or_(User.username.ilike(pattern), User.display_name.ilike(pattern)))
        .order_by(User.display_name)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "avatar": user.avatar,
        }
        for user in users
    ]
