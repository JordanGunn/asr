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


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load configuration from TOML file.

    Args:
        config_path: Override config file path. Defaults to ~/.oasr/config.toml.

    Returns:
        Configuration dictionary with defaults applied.
    """
    path = config_path or CONFIG_FILE

    # Deep copy defaults
    config = {
        "validation": DEFAULT_CONFIG["validation"].copy(),
        "adapter": DEFAULT_CONFIG["adapter"].copy(),
        "agent": DEFAULT_CONFIG["agent"].copy(),
    }

    if path.exists():
        with open(path, "rb") as f:
            loaded = tomllib.load(f)

        if "validation" in loaded:
            config["validation"].update(loaded["validation"])
        if "adapter" in loaded:
            config["adapter"].update(loaded["adapter"])
        if "agent" in loaded:
            config["agent"].update(loaded["agent"])

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
    }
