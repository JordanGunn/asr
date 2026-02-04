"""Profile listing and summary helpers."""

from __future__ import annotations

from typing import Any

from profiles.builtins import BUILTIN_PROFILE_ORDER


def sorted_profile_names(profiles: dict[str, Any]) -> list[str]:
    """Return profile names sorted with built-ins first."""
    names = sorted(profiles.keys())
    ordered = [name for name in BUILTIN_PROFILE_ORDER if name in profiles]
    remaining = [name for name in names if name not in ordered]
    return ordered + remaining


def format_profile_summary(name: str, profile: dict[str, Any]) -> str:
    """Format a single-line profile summary."""
    network = "on" if profile.get("network") else "off"
    env = "on" if profile.get("allow_env") else "off"
    shell = "on" if not profile.get("deny_shell", True) else "off"
    return f"{name:12} network={network} env={env} shell={shell}"
