"""Profile directory paths and helpers."""

from __future__ import annotations

from pathlib import Path


def get_profile_dir() -> Path:
    """Return ~/.oasr/profile directory (dynamic)."""
    try:
        from config import OASR_DIR

        return OASR_DIR / "profile"
    except Exception:
        return Path.home() / ".oasr" / "profile"


def ensure_profile_dir() -> Path:
    """Ensure ~/.oasr/profile directory exists."""
    directory = get_profile_dir()
    directory.mkdir(parents=True, exist_ok=True)
    return directory
