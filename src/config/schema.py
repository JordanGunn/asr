"""Configuration schema validation."""

from typing import Any

VALID_AGENTS = {"codex", "copilot", "claude", "opencode"}


def validate_config(config: dict[str, Any]) -> None:
    """Validate configuration dictionary.

    Args:
        config: Configuration dictionary to validate.

    Raises:
        ValueError: If configuration is invalid.
    """
    if "agent" in config and "default" in config["agent"]:
        agent = config["agent"]["default"]
        if agent is not None and agent not in VALID_AGENTS:
            raise ValueError(f"Invalid agent '{agent}'. Must be one of: {', '.join(sorted(VALID_AGENTS))}")

    if "validation" in config:
        if "reference_max_lines" in config["validation"]:
            max_lines = config["validation"]["reference_max_lines"]
            if not isinstance(max_lines, int) or max_lines < 1:
                raise ValueError("validation.reference_max_lines must be a positive integer")

        if "strict" in config["validation"]:
            if not isinstance(config["validation"]["strict"], bool):
                raise ValueError("validation.strict must be a boolean")

    if "adapter" in config:
        if "default_targets" in config["adapter"]:
            targets = config["adapter"]["default_targets"]
            if not isinstance(targets, list):
                raise ValueError("adapter.default_targets must be a list")

    if "oasr" in config:
        if "default_profile" in config["oasr"]:
            profile = config["oasr"]["default_profile"]
            if not isinstance(profile, str):
                raise ValueError("oasr.default_profile must be a string")

    if "profiles" in config:
        if not isinstance(config["profiles"], dict):
            raise ValueError("profiles must be a table (dictionary)")

        # Validate each profile structure
        for profile_name, profile_data in config["profiles"].items():
            if not isinstance(profile_data, dict):
                raise ValueError(f"Profile '{profile_name}' must be a table (dictionary)")

            # Validate profile fields if present
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
