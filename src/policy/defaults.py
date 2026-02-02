"""Safe default execution policy profile.

Conservative defaults that fail closed. Used when:
- No config exists
- Requested profile not found
- Config parsing errors occur
"""

# Safe default profile - conservative and restrictive
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
