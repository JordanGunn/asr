"""Config command - manage OASR configuration."""

import argparse
import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from agents import detect_available_agents
from config import CONFIG_FILE, get_default_config, load_config, save_config
from config.schema import validate_agent, validate_profile_reference
from profiles.builtins import BUILTIN_PROFILES
from profiles.loader import list_profile_files, load_profiles
from profiles.summary import format_profile_summary, sorted_profile_names


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the config command."""
    parser = subparsers.add_parser(
        "config",
        help="Manage configuration",
        description="Manage OASR configuration settings",
    )

    config_subparsers = parser.add_subparsers(dest="config_action", help="Config actions")

    # config set
    set_parser = config_subparsers.add_parser(
        "set",
        help="Set a configuration value",
        description="Set a configuration value",
    )
    set_parser.add_argument("key", help="Configuration key (e.g., 'agent')")
    set_parser.add_argument("value", help="Configuration value")
    set_parser.add_argument(
        "--force",
        action="store_true",
        help="Skip validation (use carefully)",
    )
    set_parser.set_defaults(func=run_set)

    # config get
    get_parser = config_subparsers.add_parser(
        "get",
        help="Get a configuration value",
        description="Get a configuration value",
    )
    get_parser.add_argument("key", help="Configuration key (e.g., 'agent')")
    get_parser.set_defaults(func=run_get)

    # config list
    list_parser = config_subparsers.add_parser(
        "list",
        help="List all configuration",
        description="List all configuration settings",
    )
    list_parser.set_defaults(func=run_list)

    # config agent
    agent_parser = config_subparsers.add_parser(
        "agent",
        help="Show agent configuration",
        description="Show default agent configuration and availability",
    )
    agent_parser.set_defaults(func=run_agent)

    # config validation
    validation_parser = config_subparsers.add_parser(
        "validation",
        help="Show validation settings",
        description="Show validation configuration settings",
    )
    validation_parser.set_defaults(func=run_validation)

    # config adapter
    adapter_parser = config_subparsers.add_parser(
        "adapter",
        help="Show adapter settings",
        description="Show adapter configuration settings",
    )
    adapter_parser.set_defaults(func=run_adapter)

    # config oasr
    oasr_parser = config_subparsers.add_parser(
        "oasr",
        help="Show core OASR settings",
        description="Show core OASR configuration settings",
    )
    oasr_parser.set_defaults(func=run_oasr)

    # config profiles
    profiles_parser = config_subparsers.add_parser(
        "profiles",
        help="Show execution profiles",
        description="Show available execution policy profiles",
    )
    profiles_parser.add_argument("--names", action="store_true", help="Output profile names only")
    profiles_parser.set_defaults(func=run_profiles)

    # config man
    man_parser = config_subparsers.add_parser(
        "man",
        help="Show configuration reference",
        description="Show configuration reference with examples",
    )
    man_parser.set_defaults(func=run_man)

    # config validate
    validate_parser = config_subparsers.add_parser(
        "validate",
        help="Validate config file",
        description="Validate configuration file structure and values",
    )
    validate_parser.set_defaults(func=run_validate)

    # config path
    path_parser = config_subparsers.add_parser(
        "path",
        help="Show config file path",
        description="Show configuration file path",
    )
    path_parser.set_defaults(func=run_path)

    # Default to showing help if no subcommand
    parser.set_defaults(func=lambda args: parser.print_help() or 1)


def _load_file_config(config_path: Path) -> dict[str, Any]:
    if config_path.exists():
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        if isinstance(data, dict):
            return data
    return {}


def _parse_key(key: str) -> tuple[str, str]:
    key = key.lower()
    aliases = {
        "agent": ("agent", "default"),
        "profile": ("oasr", "default_profile"),
    }
    if key in aliases:
        return aliases[key]
    if "." in key:
        parts = key.split(".", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid key '{key}'. Use format 'section.field' or 'agent'")
        return parts[0], parts[1]
    raise ValueError(f"Invalid key '{key}'. Use format 'section.field' or 'agent'")


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def _parse_bool(value: str, field: str) -> bool:
    value_lower = value.lower()
    if value_lower in ("true", "1", "yes", "on"):
        return True
    if value_lower in ("false", "0", "no", "off"):
        return False
    raise ValueError(f"'{field}' must be a boolean")


def run_set(args: argparse.Namespace) -> int:
    """Set a configuration value with validation."""
    key = args.key.lower()
    value = args.value
    force = getattr(args, "force", False)

    try:
        section, field = _parse_key(key)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # Type coercion based on field
    original_value = value
    try:
        if field in ("strict", "completions"):
            value = _parse_bool(value, field)
        elif field == "reference_max_lines":
            value = int(value)
            if value < 1:
                raise ValueError(f"'{field}' must be a positive integer")
        elif field == "default_targets":
            value = [item.strip() for item in value.split(",") if item.strip()]
        elif field == "default_profile":
            value = value.strip()
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # Load config
    config_path = getattr(args, "config", None)
    config_file_path = config_path or CONFIG_FILE
    config = load_config(config_path=config_path)
    file_config = _load_file_config(config_file_path)

    # Validate before setting (unless --force)
    if not force:
        # Validate agent
        if section == "agent" and field == "default":
            is_valid, error_msg = validate_agent(value)
            if not is_valid:
                print(f"Error: {error_msg}", file=sys.stderr)
                print("\nTo set anyway, use: oasr config set --force agent <name>", file=sys.stderr)
                return 1

        # Validate profile reference
        if section == "oasr" and field == "default_profile":
            is_valid, error_msg = validate_profile_reference(value, config)
            if not is_valid:
                print(f"Error: {error_msg}", file=sys.stderr)
                print("\nCreate the profile in ~/.oasr/config.toml or ~/.oasr/profile/, or use:", file=sys.stderr)
                print(f"  oasr config set --force oasr.default_profile {value}", file=sys.stderr)
                return 1

    # Set the value
    if section not in file_config:
        file_config[section] = {}

    file_config[section][field] = value

    try:
        save_config(file_config, config_path=config_file_path)

        # Show confirmation
        if section == "agent" and field == "default":
            # Special handling for agent - check if available
            available = detect_available_agents()
            if value in available:
                print(f"✓ Default agent set to: {value}")
            else:
                print(f"✓ Default agent set to: {value}")
                print(f"  Warning: '{value}' binary not found in PATH. Install it to use this agent.", file=sys.stderr)
        elif section == "oasr" and field == "default_profile":
            print(f"✓ Default profile set to: {value}")
        else:
            print(f"✓ Set {section}.{field} = {original_value}")

        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def run_get(args: argparse.Namespace) -> int:
    """Get a configuration value."""
    key = args.key.lower()

    config = load_config(args.config if hasattr(args, "config") else None)

    try:
        section, field = _parse_key(key)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    value = config.get(section, {}).get(field)
    if value is None:
        print(f"Config value not set: {section}.{field}", file=sys.stderr)
        return 1

    print(_format_value(value))
    return 0


def run_list(args: argparse.Namespace) -> int:
    """List all configuration."""
    config = load_config(args.config if hasattr(args, "config") else None)

    print("Configuration:")
    print()

    # Agent section
    print("  [agent]")
    agent = config["agent"].get("default")
    if agent:
        available = detect_available_agents()
        status = "✓" if agent in available else "✗"
        print(f"    default = {agent} {status}")
    else:
        print("    default = (not set)")
    print()

    # Show available agents
    available = detect_available_agents()
    if available:
        print(f"  Available agents: {', '.join(available)}")
    else:
        print("  Available agents: (none detected)")
    print()

    # Validation section
    print("  [validation]")
    print(f"    reference_max_lines = {config['validation']['reference_max_lines']}")
    print(f"    strict = {config['validation']['strict']}")
    print()

    # Adapter section
    print("  [adapter]")
    print(f"    default_targets = {config['adapter']['default_targets']}")
    print()

    # OASR section
    print("  [oasr]")
    print(f"    default_profile = {config['oasr']['default_profile']}")
    print(f"    completions = {_format_value(config['oasr']['completions'])}")
    print()

    # Profiles section
    print("  [profiles]")
    profiles = config.get("profiles", {})
    for name in sorted_profile_names(profiles):
        profile = profiles[name]
        summary = format_profile_summary(name, profile)
        print(f"    {summary}")
    print()

    return 0


def run_agent(args: argparse.Namespace) -> int:
    config = load_config(args.config if hasattr(args, "config") else None)
    agent = config["agent"].get("default")
    available = detect_available_agents()

    print("Agent configuration:")
    print(f"  Default: {agent or '(not set)'}")
    print()
    if available:
        print("Available agents:")
        for name in sorted(available):
            print(f"  ✓ {name}")
    else:
        print("Available agents: (none detected)")
    return 0


def run_validation(args: argparse.Namespace) -> int:
    config = load_config(args.config if hasattr(args, "config") else None)
    validation = config.get("validation", {})
    print("Validation settings:")
    print(f"  reference_max_lines: {validation.get('reference_max_lines')}")
    print(f"  strict: {validation.get('strict')}")
    return 0


def run_adapter(args: argparse.Namespace) -> int:
    config = load_config(args.config if hasattr(args, "config") else None)
    adapter = config.get("adapter", {})
    targets = adapter.get("default_targets", [])
    print("Adapter settings:")
    print(f"  default_targets: {', '.join(targets)}")
    return 0


def run_oasr(args: argparse.Namespace) -> int:
    config = load_config(args.config if hasattr(args, "config") else None)
    oasr = config.get("oasr", {})
    print("OASR settings:")
    print(f"  default_profile: {oasr.get('default_profile')}")
    print(f"  completions: {_format_value(oasr.get('completions'))}")
    return 0


def run_profiles(args: argparse.Namespace) -> int:
    config = load_config(args.config if hasattr(args, "config") else None)
    profiles = config.get("profiles", {})
    names = sorted_profile_names(profiles)

    if args.names:
        print("\n".join(names))
        return 0

    print("Profiles:")
    for name in names:
        summary = format_profile_summary(name, profiles[name])
        suffix = " (built-in)" if name in BUILTIN_PROFILES else ""
        print(f"  {summary}{suffix}")
    print("\nProfile files: ~/.oasr/profile/*.toml (inline config overrides)")
    return 0


def run_man(args: argparse.Namespace) -> int:
    print("OASR configuration reference")
    print()
    print("Quick reference:")
    print("  oasr config set <key> <value>")
    print("  oasr config get <key>")
    print("  oasr config list")
    print("  oasr config path")
    print("  oasr config validate")
    print()
    print("Common keys:")
    print("  agent")
    print("  oasr.default_profile")
    print("  oasr.completions")
    print("  validation.strict")
    print("  validation.reference_max_lines")
    print("  adapter.default_targets")
    print()
    print("Examples:")
    print("  oasr config set agent codex")
    print("  oasr config set oasr.default_profile dev")
    print("  oasr config set validation.strict true")
    print("  oasr config set adapter.default_targets cursor,windsurf")
    print()
    print("Profiles:")
    print("  - Built-ins: safe, strict, dev, unsafe")
    print("  - Inline: [profiles.<name>] in config.toml")
    print("  - Files: ~/.oasr/profile/<name>.toml (body keys only)")
    print()
    print("Docs: docs/commands/CONFIG.md and docs/configuration/README.md")
    return 0


def run_validate(args: argparse.Namespace) -> int:
    config_path = args.config if hasattr(args, "config") and args.config else CONFIG_FILE
    if not config_path.exists():
        defaults = get_default_config()
        try:
            save_config(defaults, config_path=config_path)
            print(f"✓ Created default config at {config_path}")
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    try:
        file_config = _load_file_config(config_path)
        if not isinstance(file_config, dict):
            raise ValueError("Config file must contain a table")
        inline_profiles = file_config.get("profiles", {})
        _ = load_profiles(inline_profiles=inline_profiles if isinstance(inline_profiles, dict) else {})
        save_config(file_config, config_path=config_path)
        print(f"✓ Config valid: {config_path}")
        if list_profile_files():
            print("✓ Profile files loaded")
        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def run_path(args: argparse.Namespace) -> int:
    """Show config file path."""
    if hasattr(args, "config") and args.config:
        config_path = args.config
    else:
        config_path = CONFIG_FILE
    print(config_path)
    return 0
