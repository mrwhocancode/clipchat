from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    display_name = Column(String(128), nullable=False)
    password_hash = Column(String(256), nullable=False)
    avatar = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    sent_messages = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    conversation_user1 = relationship(
        "Conversation",
        back_populates="user1",
        foreign_keys="Conversation.user1_id",
        cascade="all, delete-orphan",
    )
    conversation_user2 = relationship(
        "Conversation",
        back_populates="user2",
        foreign_keys="Conversation.user2_id",
        cascade="all, delete-orphan",
    )
