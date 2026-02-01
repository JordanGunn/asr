"""Default configuration values."""

from typing import Any

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
}
