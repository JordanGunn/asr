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
