"""Default configuration values."""

from typing import Any

from profiles.builtins import BUILTIN_PROFILES

DEFAULT_CONFIG: dict[str, Any] = {
    "validation": {
        "reference_max_lines": 500,
        "strict": False,
    },
    "adapter": {
        "default_targets": ["cursor", "windsurf"],
    },
    "agent": {
        "default": None,
    },
    "oasr": {
        "default_profile": "safe",
        "completions": True,
    },
    "profiles": {name: values.copy() for name, values in BUILTIN_PROFILES.items()},
}
