"""Profile validation helpers."""

from __future__ import annotations

from typing import Any


def validate_profile_data(profile_name: str, profile_data: dict[str, Any]) -> None:
    """Validate a single profile data structure."""
    if "fs_read_roots" in profile_data and not isinstance(profile_data["fs_read_roots"], list):
        raise ValueError(f"Profile '{profile_name}': fs_read_roots must be a list")
    if "fs_write_roots" in profile_data and not isinstance(profile_data["fs_write_roots"], list):
        raise ValueError(f"Profile '{profile_name}': fs_write_roots must be a list")
    if "deny_paths" in profile_data and not isinstance(profile_data["deny_paths"], list):
        raise ValueError(f"Profile '{profile_name}': deny_paths must be a list")
    if "allowed_commands" in profile_data and not isinstance(profile_data["allowed_commands"], list):
        raise ValueError(f"Profile '{profile_name}': allowed_commands must be a list")
    if "deny_shell" in profile_data and not isinstance(profile_data["deny_shell"], bool):
        raise ValueError(f"Profile '{profile_name}': deny_shell must be a boolean")
    if "network" in profile_data and not isinstance(profile_data["network"], bool):
        raise ValueError(f"Profile '{profile_name}': network must be a boolean")
    if "allow_env" in profile_data and not isinstance(profile_data["allow_env"], bool):
        raise ValueError(f"Profile '{profile_name}': allow_env must be a boolean")


def validate_profiles(profiles: dict[str, Any]) -> None:
    """Validate profile map structure."""
    if not isinstance(profiles, dict):
        raise ValueError("profiles must be a table (dictionary)")

    for profile_name, profile_data in profiles.items():
        if not isinstance(profile_data, dict):
            raise ValueError(f"Profile '{profile_name}' must be a table (dictionary)")
        validate_profile_data(profile_name, profile_data)
