"""Profile loading and merging utilities."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from profiles.builtins import BUILTIN_PROFILES
from profiles.paths import get_profile_dir


def list_profile_files(profile_dir: Path | None = None) -> list[Path]:
    """Return profile files from ~/.oasr/profile."""
    directory = profile_dir or get_profile_dir()
    if not directory.exists():
        return []
    return sorted(p for p in directory.glob("*.toml") if p.is_file())


def load_profile_file(path: Path) -> dict[str, Any]:
    """Load a profile TOML file containing only profile keys."""
    with open(path, "rb") as f:
        data = tomllib.load(f)
    if not isinstance(data, dict):
        raise ValueError("Profile file must contain a table of profile settings")
    return data


def load_profile_files(profile_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load profile files into a name->profile map."""
    profiles: dict[str, dict[str, Any]] = {}
    for path in list_profile_files(profile_dir):
        name = path.stem
        try:
            profiles[name] = load_profile_file(path)
        except Exception as exc:
            print(f"⚠ Warning: Failed to load profile '{name}': {exc}", file=sys.stderr)
    return profiles


def merge_profiles(
    builtin: dict[str, dict[str, Any]],
    file_profiles: dict[str, dict[str, Any]],
    inline_profiles: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Merge profiles with precedence: inline > file > builtin."""
    merged: dict[str, dict[str, Any]] = {}
    for source in (builtin, file_profiles, inline_profiles):
        for name, profile in source.items():
            merged[name] = profile.copy()
    return merged


def merge_profile_data(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    """Merge profile values with override precedence."""
    merged = base.copy()
    merged.update(overrides)
    return merged


def load_profiles(
    inline_profiles: dict[str, dict[str, Any]] | None = None,
    profile_dir: Path | None = None,
) -> dict[str, dict[str, Any]]:
    """Load merged profiles from builtin + profile files + inline config."""
    inline_profiles = inline_profiles or {}
    file_profiles = load_profile_files(profile_dir)
    return merge_profiles(BUILTIN_PROFILES, file_profiles, inline_profiles)
