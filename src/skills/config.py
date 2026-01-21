"""Configuration management for ~/.skills/config.toml."""

import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w

SKILLS_DIR = Path.home() / ".skills"
CONFIG_FILE = SKILLS_DIR / "config.toml"

DEFAULT_CONFIG: dict[str, Any] = {
    "validation": {
        "reference_max_lines": 500,
        "strict": False,
    },
    "adapter": {
        "default_targets": ["cursor", "windsurf"],
    },
}


def ensure_skills_dir() -> Path:
    """Ensure ~/.skills/ directory exists."""
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    return SKILLS_DIR


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load configuration from TOML file.
    
    Args:
        config_path: Override config file path. Defaults to ~/.skills/config.toml.
    
    Returns:
        Configuration dictionary with defaults applied.
    """
    path = config_path or CONFIG_FILE
    
    config = DEFAULT_CONFIG.copy()
    config["validation"] = DEFAULT_CONFIG["validation"].copy()
    config["adapter"] = DEFAULT_CONFIG["adapter"].copy()
    
    if path.exists():
        with open(path, "rb") as f:
            loaded = tomllib.load(f)
        
        if "validation" in loaded:
            config["validation"].update(loaded["validation"])
        if "adapter" in loaded:
            config["adapter"].update(loaded["adapter"])
    
    return config


def save_config(config: dict[str, Any], config_path: Path | None = None) -> None:
    """Save configuration to TOML file.
    
    Args:
        config: Configuration dictionary to save.
        config_path: Override config file path. Defaults to ~/.skills/config.toml.
    """
    path = config_path or CONFIG_FILE
    ensure_skills_dir()
    
    with open(path, "wb") as f:
        tomli_w.dump(config, f)


def get_default_config() -> dict[str, Any]:
    """Return a copy of the default configuration."""
    config = DEFAULT_CONFIG.copy()
    config["validation"] = DEFAULT_CONFIG["validation"].copy()
    config["adapter"] = DEFAULT_CONFIG["adapter"].copy()
    return config
