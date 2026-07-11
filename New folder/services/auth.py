from __future__ import annotations

from typing import Optional

import bcrypt
from fastapi import Request
from sqlalchemy.orm import Session

from models.user import User

pwd_context = None  # kept for backward compatibility in imports; hashing uses bcrypt directly


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, username: str, display_name: str, password: str) -> User:
    username = username.strip()
    display_name = display_name.strip()
    if not username or not display_name:
        raise ValueError("Username and display name are required")

    password_hash = hash_password(password)
    user = User(username=username, display_name=display_name, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def get_session_user_id(request: Request) -> Optional[int]:
    user_id = request.session.get("user_id")
    return int(user_id) if user_id is not None else None


def get_current_user_from_request(request: Request, db: Session) -> Optional[User]:
    user_id = get_session_user_id(request)
    if not user_id:
        return None
    return get_user_by_id(db, user_id)
