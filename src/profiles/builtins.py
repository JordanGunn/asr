"""Built-in execution policy profiles."""

from __future__ import annotations

from typing import Any

SAFE = {
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
}

STRICT = {
    "fs_read_roots": ["./"],
    "fs_write_roots": ["./.oasr"],
    "deny_paths": SAFE["deny_paths"],
    "allowed_commands": ["rg", "cat"],
    "deny_shell": True,
    "network": False,
    "allow_env": False,
}

DEV = {
    "fs_read_roots": ["./", "~/projects"],
    "fs_write_roots": ["./", "./out", "./.oasr", "~/projects"],
    "deny_paths": SAFE["deny_paths"],
    "allowed_commands": ["bash", "python", "node", "git", "curl", "rg", "fd", "jq", "cat", "npm", "pip"],
    "deny_shell": False,
    "network": True,
    "allow_env": True,
}

UNSAFE = {
    "fs_read_roots": ["/"],
    "fs_write_roots": ["/"],
    "deny_paths": [],
    "allowed_commands": ["*"],
    "deny_shell": False,
    "network": True,
    "allow_env": True,
}

BUILTIN_PROFILES: dict[str, dict[str, Any]] = {
    "safe": SAFE,
    "strict": STRICT,
    "dev": DEV,
    "unsafe": UNSAFE,
}

BUILTIN_PROFILE_ORDER = ("safe", "strict", "dev", "unsafe")

BUILTIN_DESCRIPTIONS: dict[str, str] = {
    "safe": "Conservative defaults for most workflows.",
    "strict": "Minimal access, no network, no shell.",
    "dev": "Permissive for local development.",
    "unsafe": "Full access to system and commands.",
}


def is_builtin_profile(name: str) -> bool:
    """Return True if name is a built-in profile."""
    return name in BUILTIN_PROFILES
