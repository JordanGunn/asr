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


def normalize_profile_name(name: str) -> str:
    """Normalize profile names to kebab-case."""
    lowered = name.strip().lower().replace("_", "-").replace(" ", "-")
    sanitized = []
    prev_dash = False
    for ch in lowered:
        if ch.isalnum() or ch == "-":
            if ch == "-":
                if prev_dash:
                    continue
                prev_dash = True
            else:
                prev_dash = False
            sanitized.append(ch)
    normalized = "".join(sanitized).strip("-")
    return normalized or "profile"


def render_profile_template(data: dict[str, Any]) -> str:
    """Render a commented TOML template for a profile."""

    def fmt_list(values: list[str]) -> str:
        items = ", ".join(f'"{item}"' for item in values)
        return f"[{items}]"

    defaults = {
        "fs_read_roots": ["./"],
        "fs_write_roots": ["./out", "./.oasr"],
        "deny_paths": ["~/.ssh", "~/.aws", "**/.env", "**/secrets/**"],
        "allowed_commands": ["rg", "fd", "jq", "cat"],
        "deny_shell": True,
        "network": False,
        "allow_env": False,
    }

    merged = defaults.copy()
    merged.update(data)

    lines = [
        "# Profile settings for OASR execution policies.",
        "# Paths are recursive by default.",
        "",
        "# Directories allowed for READ access",
        f"fs_read_roots = {fmt_list(merged['fs_read_roots'])}",
        "",
        "# Directories allowed for WRITE access",
        f"fs_write_roots = {fmt_list(merged['fs_write_roots'])}",
        "",
        "# Denied paths (glob patterns supported)",
        f"deny_paths = {fmt_list(merged['deny_paths'])}",
        "",
        '# Whitelisted commands (use ["*"] for all)',
        f"allowed_commands = {fmt_list(merged['allowed_commands'])}",
        "",
        "# Deny all shell execution (true/false)",
        f"deny_shell = {str(merged['deny_shell']).lower()}",
        "",
        "# Allow outbound network access (true/false)",
        f"network = {str(merged['network']).lower()}",
        "",
        "# Allow reading environment variables (true/false)",
        f"allow_env = {str(merged['allow_env']).lower()}",
        "",
    ]
    return "\n".join(lines)
