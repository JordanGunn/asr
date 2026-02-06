"""Profile loading utilities for OASR."""

from profiles.builtins import BUILTIN_DESCRIPTIONS, BUILTIN_PROFILE_ORDER, BUILTIN_PROFILES, is_builtin_profile
from profiles.loader import delete_profile, get_profile_path, load_profiles, merge_profile_data, save_profile
from profiles.paths import ensure_profile_dir, get_profile_dir
from profiles.registry import get_profiles, list_profiles
from profiles.summary import (
    format_profile_summary,
    normalize_profile_name,
    render_profile_template,
    sorted_profile_names,
)
from profiles.validation import validate_profile_data, validate_profiles

__all__ = [
    "BUILTIN_PROFILES",
    "BUILTIN_PROFILE_ORDER",
    "BUILTIN_DESCRIPTIONS",
    "is_builtin_profile",
    "load_profiles",
    "get_profile_dir",
    "ensure_profile_dir",
    "format_profile_summary",
    "get_profiles",
    "list_profiles",
    "get_profile_path",
    "save_profile",
    "delete_profile",
    "merge_profile_data",
    "sorted_profile_names",
    "normalize_profile_name",
    "render_profile_template",
    "validate_profile_data",
    "validate_profiles",
]
