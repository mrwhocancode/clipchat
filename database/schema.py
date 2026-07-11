from __future__ import annotations

from database.db import Base, engine

# Import models so SQLAlchemy registers tables before create_all runs.
from models import conversation, message, user  # noqa: F401


def create_tables() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
