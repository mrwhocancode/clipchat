from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from services.auth import get_user_by_id
from services.chat import create_message, get_or_create_conversation, serialize_message

CLIPS_DIR = Path("static/clips")
CLIP_CATALOG_FILE = CLIPS_DIR / "catalog.json"
ALLOWED_CLIP_EXTENSIONS = {".mp4", ".webm", ".mov"}


def list_available_clips() -> list[str]:
    """Return clip filenames available in static/clips/."""
    if not CLIPS_DIR.exists():
        return []

    clips = []
    for entry in sorted(CLIPS_DIR.iterdir()):
        if entry.is_file() and entry.suffix.lower() in ALLOWED_CLIP_EXTENSIONS:
            clips.append(entry.name)
    return clips


def _load_clip_catalog() -> dict[str, dict[str, str]]:
    """Load optional local dialogue metadata keyed by clip filename."""
    if not CLIP_CATALOG_FILE.is_file():
        return {}

    try:
        raw_catalog = json.loads(CLIP_CATALOG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    entries = raw_catalog.get("clips", []) if isinstance(raw_catalog, dict) else []
    if not isinstance(entries, list):
        return {}

    catalog: dict[str, dict[str, str]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        clip_id = entry.get("clip_id")
        if not isinstance(clip_id, str) or not validate_clip_id(clip_id):
            continue
        catalog[clip_id] = {
            "title": str(entry.get("title", Path(clip_id).stem)),
            "transcript": str(entry.get("transcript", "")),
            "keywords": str(entry.get("keywords", "")),
        }
    return catalog


def search_available_clips(query: str, limit: int = 20) -> list[dict[str, str]]:
    """Search local, licensed clips by filename, transcript, and catalog keywords."""
    normalized_query = query.strip().casefold()
    if not normalized_query:
        return []

    catalog = _load_clip_catalog()
    matches: list[dict[str, str]] = []
    for clip_id in list_available_clips():
        metadata = catalog.get(clip_id, {})
        searchable_text = " ".join(
            (clip_id, metadata.get("title", ""), metadata.get("transcript", ""), metadata.get("keywords", ""))
        ).casefold()
        if normalized_query not in searchable_text:
            continue
        matches.append(
            {
                "clip_id": clip_id,
                "title": metadata.get("title", Path(clip_id).stem),
                "transcript": metadata.get("transcript", ""),
            }
        )
        if len(matches) >= limit:
            break

    return matches


def validate_clip_id(clip_id: str) -> bool:
    """Ensure the clip exists locally and path traversal is blocked."""
    if not clip_id or "/" in clip_id or "\\" in clip_id or clip_id.startswith("."):
        return False

    clip_path = (CLIPS_DIR / clip_id).resolve()
    clips_root = CLIPS_DIR.resolve()
    if clips_root not in clip_path.parents:
        return False
    if not clip_path.is_file():
        return False

    return clip_path.suffix.lower() in ALLOWED_CLIP_EXTENSIONS


def send_clip(db: Session, sender_id: int, receiver_id: int, clip_id: str) -> dict[str, Any]:
    """Create or reuse a conversation, store the clip message, and return payload."""
    if sender_id == receiver_id:
        raise ValueError("Cannot send a clip to yourself")

    if not get_user_by_id(db, receiver_id):
        raise ValueError("Receiver does not exist")

    if not validate_clip_id(clip_id):
        raise ValueError("Invalid clip_id")

    conversation = get_or_create_conversation(db, sender_id, receiver_id)
    message = create_message(db, conversation.id, sender_id, clip_id)
    return serialize_message(message)
