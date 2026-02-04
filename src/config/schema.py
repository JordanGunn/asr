"""Configuration schema validation."""

from typing import Any

from profiles.validation import validate_profiles

VALID_AGENTS = {"codex", "copilot", "claude", "opencode"}


def validate_agent(agent: str | None) -> tuple[bool, str | None]:
    """Validate agent configuration value.

    Args:
        agent: Agent name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if agent is None:
        return (True, None)

    if agent not in VALID_AGENTS:
        sorted_agents = ", ".join(sorted(VALID_AGENTS))
        return (False, f"Invalid agent '{agent}'. Valid agents: {sorted_agents}")

    return (True, None)


def validate_profile_reference(profile_name: str, config: dict[str, Any]) -> tuple[bool, str | None]:
    """Validate that a profile reference exists in config.

    Args:
        profile_name: Profile name to validate
        config: Full config dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    profiles = config.get("profiles", {})

    if profile_name not in profiles:
        available = ", ".join(sorted(profiles.keys()))
        return (False, f"Profile '{profile_name}' not found. Available profiles: {available}")

    return (True, None)


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
        validate_profiles(config["profiles"])
