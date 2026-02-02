"""Policy profile definitions and loading.

Defines what agents can do during skill execution. Profiles are user-defined
in config.toml and enforced at runtime.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from policy.defaults import SAFE


@dataclass
class Profile:
    """Execution policy profile defining agent capabilities and restrictions.

    Attributes:
        name: Profile identifier (e.g., "safe", "dev")
        fs_read_roots: Allowed filesystem read locations
        fs_write_roots: Allowed filesystem write locations
        deny_paths: Explicitly denied paths (takes precedence)
        allowed_commands: Permitted shell commands
        deny_shell: If True, deny all shell/subprocess execution
        network: Allow network access
        allow_env: Allow reading environment variables
    """

    name: str
    fs_read_roots: list[str] = field(default_factory=lambda: ["./"])
    fs_write_roots: list[str] = field(default_factory=lambda: ["./out", "./.oasr"])
    deny_paths: list[str] = field(
        default_factory=lambda: [
            "~/.ssh",
            "~/.aws",
            "~/.gnupg",
            "~/.config",
            ".env",
            "~/.bashrc",
            "~/.zshrc",
            "~/.profile",
        ]
    )
    allowed_commands: list[str] = field(default_factory=lambda: ["rg", "fd", "jq", "cat"])
    deny_shell: bool = True
    network: bool = False
    allow_env: bool = False

    def __post_init__(self):
        """Resolve and normalize paths after initialization."""
        self.fs_read_roots = [self._resolve_path(p) for p in self.fs_read_roots]
        self.fs_write_roots = [self._resolve_path(p) for p in self.fs_write_roots]
        self.deny_paths = [self._resolve_path(p) for p in self.deny_paths]

    def _resolve_path(self, path: str) -> str:
        """Resolve path: expand ~, make absolute if relative to cwd.

        Relative paths are workspace-relative (relative to current directory).
        Tilde (~) is expanded to user home directory.

        Args:
            path: Path string (may contain ~, be relative or absolute)

        Returns:
            Normalized absolute path string
        """
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = Path.cwd() / p
        return str(p.resolve())


def load(config: dict[str, Any], profile_name: str, cwd: Path | None = None) -> Profile:
    """Load a policy profile from config with fallback to safe defaults.

    Args:
        config: Full config dict (may contain profiles.<name> tables)
        profile_name: Name of profile to load (e.g., "safe", "dev")
        cwd: Working directory for relative path resolution (default: current)

    Returns:
        Profile with merged defaults + user overrides

    Notes:
        - Missing profiles fall back to hardcoded safe defaults
        - Malformed config falls back to safe + logs warning
        - All paths are resolved to absolute paths
        - Fail-closed behavior: errors → safe defaults
    """
    if cwd:
        # Temporarily change directory context for path resolution
        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(cwd)
            return _load_impl(config, profile_name)
        finally:
            os.chdir(old_cwd)
    else:
        return _load_impl(config, profile_name)


def _load_impl(config: dict[str, Any], profile_name: str) -> Profile:
    """Internal implementation of load()."""
    # Start with safe defaults
    profile_data = SAFE.copy()

    # Try to load user-defined profile
    try:
        profiles = config.get("profiles", {})
        if profile_name in profiles:
            user_profile = profiles[profile_name]
            # Merge user overrides
            for key in SAFE.keys():
                if key in user_profile:
                    profile_data[key] = user_profile[key]
        elif profile_name != "safe":
            # Warn if non-safe profile doesn't exist, but continue with safe defaults
            print(
                f"⚠ Warning: Profile '{profile_name}' not found in config. Using 'safe' defaults.",
                file=sys.stderr,
            )
    except Exception as e:
        # Fail closed: any error in config parsing → safe defaults
        print(
            f"⚠ Warning: Error loading profile config: {e}. Using 'safe' defaults.",
            file=sys.stderr,
        )

    return Profile(name=profile_name, **profile_data)


def summarize(profile: Profile, skill_name: str, agent_name: str) -> str:
    """Generate human-readable policy summary for confirmation prompt.

    Args:
        profile: Policy profile to summarize
        skill_name: Name of skill being executed
        agent_name: Name of agent being used

    Returns:
        Formatted multi-line string suitable for stderr output
    """
    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "EXECUTION POLICY REVIEW",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"Skill:             {skill_name}",
        f"Agent:             {agent_name}",
        f"Profile:           {profile.name}",
        f"Network:           {'allowed' if profile.network else 'denied'}",
        f"Environment:       {'allowed' if profile.allow_env else 'denied'}",
        f"Shell:             {'allowed' if not profile.deny_shell else 'denied'}",
    ]

    # Format allowed commands (truncate if too long)
    if profile.allowed_commands:
        commands = ", ".join(profile.allowed_commands)
        if len(commands) > 60:
            commands = commands[:57] + "..."
        lines.append(f"Allowed commands:  {commands}")
    else:
        lines.append("Allowed commands:  (none)")

    # Format paths (show first few, indicate if more)
    lines.append(f"Read roots:        {', '.join(profile.fs_read_roots[:3])}")
    if len(profile.fs_read_roots) > 3:
        lines.append(f"                   ... and {len(profile.fs_read_roots) - 3} more")

    lines.append(f"Write roots:       {', '.join(profile.fs_write_roots[:3])}")
    if len(profile.fs_write_roots) > 3:
        lines.append(f"                   ... and {len(profile.fs_write_roots) - 3} more")

    # Show some deny paths (not all - could be long)
    if profile.deny_paths:
        deny_sample = profile.deny_paths[:5]
        lines.append(f"Deny paths:        {', '.join(deny_sample)}")
        if len(profile.deny_paths) > 5:
            lines.append(f"                   ... and {len(profile.deny_paths) - 5} more")

    return "\n".join(lines)
