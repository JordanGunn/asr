"""Profile registry operations."""

from __future__ import annotations

from typing import Any

from profiles.loader import load_profiles
from profiles.summary import sorted_profile_names


def list_profiles(inline_profiles: dict[str, dict[str, Any]] | None = None) -> list[str]:
    """Return ordered profile names with all sources merged."""
    profiles = load_profiles(inline_profiles=inline_profiles or {})
    return sorted_profile_names(profiles)


def get_profiles(inline_profiles: dict[str, dict[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
    """Return merged profiles."""
    return load_profiles(inline_profiles=inline_profiles or {})
