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
    "oasr": {
        "default_profile": "safe",
    },
    "profiles": {
        # Built-in safe profile (always available as fallback)
        "safe": {
            "fs_read_roots": ["./"],
            "fs_write_roots": ["./out", "./.oasr"],
            "deny_paths": [
                "~/.ssh",
                "~/.aws",
                "~/.gnupg",
                "~/.config",
                ".env",
                "~/.bashrc",
                "~/.zshrc",
                "~/.profile",
            ],
            "allowed_commands": ["rg", "fd", "jq", "cat"],
            "deny_shell": True,
            "network": False,
            "allow_env": False,
        },
    },
}
