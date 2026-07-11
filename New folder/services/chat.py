from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.conversation import Conversation
from models.message import Message
from models.user import User


def normalize_user_pair(user_a_id: int, user_b_id: int) -> tuple[int, int]:
    """Store conversations with the lower user id as user1 for consistent lookup."""
    if user_a_id == user_b_id:
        raise ValueError("Cannot create a conversation with yourself")
    return (user_a_id, user_b_id) if user_a_id < user_b_id else (user_b_id, user_a_id)


def get_conversation_between(db: Session, user_a_id: int, user_b_id: int) -> Optional[Conversation]:
    user1_id, user2_id = normalize_user_pair(user_a_id, user_b_id)
    return (
        db.query(Conversation)
        .filter(Conversation.user1_id == user1_id, Conversation.user2_id == user2_id)
        .first()
    )


def get_or_create_conversation(db: Session, user_a_id: int, user_b_id: int) -> Conversation:
    conversation = get_conversation_between(db, user_a_id, user_b_id)
    if conversation:
        return conversation

    user1_id, user2_id = normalize_user_pair(user_a_id, user_b_id)
    conversation = Conversation(user1_id=user1_id, user2_id=user2_id)
    db.add(conversation)
    try:
        db.commit()
    except IntegrityError:
        # Another request created the same pair after the lookup above.
        db.rollback()
        existing = get_conversation_between(db, user_a_id, user_b_id)
        if existing:
            return existing
        raise
    db.refresh(conversation)
    return conversation


def get_conversation_by_id(db: Session, conversation_id: int) -> Optional[Conversation]:
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def user_in_conversation(conversation: Conversation, user_id: int) -> bool:
    return user_id in (conversation.user1_id, conversation.user2_id)


def get_other_user_id(conversation: Conversation, user_id: int) -> Optional[int]:
    if conversation.user1_id == user_id:
        return conversation.user2_id
    if conversation.user2_id == user_id:
        return conversation.user1_id
    return None


def get_other_user(db: Session, conversation: Conversation, user_id: int) -> Optional[User]:
    other_user_id = get_other_user_id(conversation, user_id)
    if not other_user_id:
        return None
    return db.query(User).filter(User.id == other_user_id).first()


def get_messages_for_conversation(db: Session, conversation_id: int, user_id: int) -> list[dict[str, Any]]:
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation or not user_in_conversation(conversation, user_id):
        return []

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    return [
        {
            "id": message.id,
            "sender_id": message.sender_id,
            "clip_id": message.clip_id,
            "created_at": message.created_at.isoformat(),
        }
        for message in messages
    ]


def create_message(db: Session, conversation_id: int, sender_id: int, clip_id: str) -> Message:
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation or not user_in_conversation(conversation, sender_id):
        raise PermissionError("User is not part of this conversation")

    message = Message(conversation_id=conversation_id, sender_id=sender_id, clip_id=clip_id)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def serialize_message(message: Message) -> dict[str, Any]:
    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "sender_id": message.sender_id,
        "clip_id": message.clip_id,
        "created_at": message.created_at.isoformat(),
    }


def get_conversations_for_user(db: Session, user_id: int) -> list[dict[str, Any]]:
    conversations = (
        db.query(Conversation)
        .filter(or_(Conversation.user1_id == user_id, Conversation.user2_id == user_id))
        .order_by(Conversation.created_at.desc())
        .all()
    )

    results: list[dict[str, Any]] = []
    for conversation in conversations:
        other_user = get_other_user(db, conversation, user_id)
        if not other_user:
            continue

        last_message = (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .first()
        )

        results.append(
            {
                "id": conversation.id,
                "other_user": {
                    "id": other_user.id,
                    "username": other_user.username,
                    "display_name": other_user.display_name,
                    "avatar": other_user.avatar,
                },
                "last_message": serialize_message(last_message) if last_message else None,
                "created_at": conversation.created_at.isoformat(),
            }
        )

    return results
