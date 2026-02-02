"""Configuration management for ~/.oasr/config.toml."""

import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w

from config.defaults import DEFAULT_CONFIG
from config.env import load_env_config, merge_configs
from config.schema import validate_config

OASR_DIR = Path.home() / ".oasr"
CONFIG_FILE = OASR_DIR / "config.toml"

__all__ = [
    "OASR_DIR",
    "CONFIG_FILE",
    "ensure_oasr_dir",
    "ensure_skills_dir",
    "load_config",
    "save_config",
    "get_default_config",
]


def ensure_oasr_dir() -> Path:
    """Ensure ~/.oasr/ directory exists."""
    OASR_DIR.mkdir(parents=True, exist_ok=True)
    return OASR_DIR


# Legacy alias for backwards compatibility
def ensure_skills_dir() -> Path:
    """Legacy alias for ensure_oasr_dir()."""
    return ensure_oasr_dir()


def load_config(
    config_path: Path | None = None, cli_overrides: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Load configuration from multiple sources with precedence.

    Precedence order (highest to lowest):
        1. cli_overrides - explicit CLI flags
        2. Environment variables (OASR_*)
        3. Config file (~/.oasr/config.toml)
        4. Built-in defaults

    Args:
        config_path: Override config file path. Defaults to ~/.oasr/config.toml.
        cli_overrides: Optional CLI flag overrides (highest precedence)

    Returns:
        Merged configuration dictionary with all sources applied.
    """
    path = config_path or CONFIG_FILE
    cli_overrides = cli_overrides or {}

    # Deep copy defaults
    defaults = {
        "validation": DEFAULT_CONFIG["validation"].copy(),
        "adapter": DEFAULT_CONFIG["adapter"].copy(),
        "agent": DEFAULT_CONFIG["agent"].copy(),
        "oasr": DEFAULT_CONFIG["oasr"].copy(),
        "profiles": {k: v.copy() for k, v in DEFAULT_CONFIG["profiles"].items()},
    }

    # Load config file
    file_config = {}
    if path.exists():
        with open(path, "rb") as f:
            file_config = tomllib.load(f)

    # Load environment variables
    env_config = load_env_config()

    # Merge all sources with precedence
    config = merge_configs(
        cli_overrides=cli_overrides,
        env_config=env_config,
        file_config=file_config,
        defaults=defaults,
    )

    return config


def save_config(config: dict[str, Any], config_path: Path | None = None) -> None:
    """Save configuration to TOML file.

    Args:
        config: Configuration dictionary to save.
        config_path: Override config file path. Defaults to ~/.oasr/config.toml.

    Raises:
        ValueError: If configuration is invalid.
    """
    validate_config(config)

    path = config_path or CONFIG_FILE
    ensure_oasr_dir()

    # Deep copy and remove None values (TOML can't serialize None)
    config_to_save = {}
    for section, values in config.items():
        if isinstance(values, dict):
            config_to_save[section] = {k: v for k, v in values.items() if v is not None}
        else:
            if values is not None:
                config_to_save[section] = values

    with open(path, "wb") as f:
        tomli_w.dump(config_to_save, f)


def get_default_config() -> dict[str, Any]:
    """Return a copy of the default configuration."""
    return {
        "validation": DEFAULT_CONFIG["validation"].copy(),
        "adapter": DEFAULT_CONFIG["adapter"].copy(),
        "agent": DEFAULT_CONFIG["agent"].copy(),
        "oasr": DEFAULT_CONFIG["oasr"].copy(),
        "profiles": {k: v.copy() for k, v in DEFAULT_CONFIG["profiles"].items()},
    }
