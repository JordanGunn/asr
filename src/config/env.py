"""Environment variable configuration support.

This module provides functionality to load OASR configuration from environment
variables, following the pattern: OASR_<SECTION>_<KEY>

Precedence order:
    1. CLI flags (highest)
    2. Environment variables
    3. Config file
    4. Built-in defaults (lowest)

Environment variable naming:
    - Prefix: OASR_
    - Format: OASR_<SECTION>_<KEY> (uppercase, underscore-separated)
    - Examples:
        OASR_AGENT=codex             → agent.default = "codex"
        OASR_PROFILE=dev             → oasr.default_profile = "dev"
        OASR_VALIDATION_STRICT=true  → validation.strict = true

Type handling:
    - Strings: as-is
    - Booleans: true/false, 1/0, yes/no, on/off (case-insensitive)
    - Integers: parsed with int()
    - Lists: comma-separated values
"""

import os
from typing import Any

# Mapping of environment variable names to config paths
ENV_VAR_MAP = {
    "OASR_AGENT": ("agent", "default"),
    "OASR_PROFILE": ("oasr", "default_profile"),
    "OASR_VALIDATION_STRICT": ("validation", "strict"),
    "OASR_VALIDATION_MAX_LINES": ("validation", "reference_max_lines"),
    "OASR_ADAPTER_TARGETS": ("adapter", "default_targets"),
}


def parse_bool(value: str) -> bool:
    """Parse boolean from string.

    Args:
        value: String value to parse

    Returns:
        Boolean value

    Raises:
        ValueError: If value cannot be parsed as boolean
    """
    value_lower = value.lower()
    if value_lower in ("true", "1", "yes", "on"):
        return True
    if value_lower in ("false", "0", "no", "off"):
        return False
    raise ValueError(f"Cannot parse '{value}' as boolean")


def parse_int(value: str) -> int:
    """Parse integer from string.

    Args:
        value: String value to parse

    Returns:
        Integer value

    Raises:
        ValueError: If value cannot be parsed as integer
    """
    return int(value)


def parse_list(value: str) -> list[str]:
    """Parse list from comma-separated string.

    Args:
        value: Comma-separated string

    Returns:
        List of strings (trimmed)
    """
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_value(value: str, expected_type: type) -> Any:
    """Parse environment variable value based on expected type.

    Args:
        value: String value from environment
        expected_type: Expected Python type

    Returns:
        Parsed value of appropriate type

    Raises:
        ValueError: If value cannot be parsed to expected type
    """
    if expected_type is bool:
        return parse_bool(value)
    elif expected_type is int:
        return parse_int(value)
    elif expected_type is list:
        return parse_list(value)
    else:
        return value  # String, return as-is


def load_env_config() -> dict[str, dict[str, Any]]:
    """Load configuration from environment variables.

    Reads all OASR_* environment variables and converts them to a nested
    dictionary structure matching the config file format.

    Returns:
        Nested dictionary with config values from environment variables
        Example: {"agent": {"default": "codex"}, "oasr": {"default_profile": "safe"}}

    Notes:
        - Only processes variables defined in ENV_VAR_MAP
        - Silently skips variables with invalid values (logs warning)
        - Returns empty sections if no relevant env vars set
    """
    config = {}

    for env_var, (section, key) in ENV_VAR_MAP.items():
        value = os.getenv(env_var)
        if value is None:
            continue

        # Determine expected type based on key
        # This is a heuristic - we infer type from key name
        expected_type = str  # Default
        if key == "strict":
            expected_type = bool
        elif key == "reference_max_lines":
            expected_type = int
        elif key == "default_targets":
            expected_type = list

        try:
            parsed_value = parse_value(value, expected_type)

            # Create section if it doesn't exist
            if section not in config:
                config[section] = {}

            config[section][key] = parsed_value

        except (ValueError, TypeError) as e:
            # Log warning but continue (fail-safe)
            import sys

            print(
                f"⚠ Warning: Invalid value for {env_var}='{value}': {e}. Skipping.",
                file=sys.stderr,
            )
            continue

    return config


def merge_configs(
    cli_overrides: dict[str, Any],
    env_config: dict[str, dict[str, Any]],
    file_config: dict[str, dict[str, Any]],
    defaults: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Merge configurations from multiple sources with correct precedence.

    Precedence order (highest to lowest):
        1. cli_overrides - explicit CLI flags
        2. env_config - environment variables
        3. file_config - config file values
        4. defaults - built-in defaults

    Args:
        cli_overrides: Values explicitly set via CLI flags
        env_config: Values from environment variables
        file_config: Values from config file
        defaults: Built-in default values

    Returns:
        Merged configuration dictionary

    Notes:
        - CLI overrides take precedence over everything
        - Environment variables override config file
        - Config file overrides defaults
        - Sections are merged independently
    """
    result = {}

    # Get all sections from all sources
    all_sections = set()
    for config in [defaults, file_config, env_config, cli_overrides]:
        all_sections.update(config.keys())

    # Merge each section with precedence
    for section in all_sections:
        result[section] = {}

        # Start with defaults
        if section in defaults:
            result[section].update(defaults[section])

        # Override with file config
        if section in file_config:
            result[section].update(file_config[section])

        # Override with env config
        if section in env_config:
            result[section].update(env_config[section])

        # Override with CLI (if present)
        if section in cli_overrides:
            result[section].update(cli_overrides[section])

    return result


def get_config_source(
    section: str,
    key: str,
    cli_overrides: dict[str, Any],
    env_config: dict[str, dict[str, Any]],
    file_config: dict[str, dict[str, Any]],
) -> str:
    """Determine the source of a config value.

    Args:
        section: Config section name
        key: Config key name
        cli_overrides: CLI flag overrides
        env_config: Environment variable config
        file_config: Config file values

    Returns:
        Source string: "cli flag", "env var", "config file", or "default"
    """
    if section in cli_overrides and key in cli_overrides[section]:
        return "cli flag"
    if section in env_config and key in env_config.get(section, {}):
        return "env var"
    if section in file_config and key in file_config.get(section, {}):
        return "config file"
    return "default"
