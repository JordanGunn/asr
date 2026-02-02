"""Config command - manage OASR configuration."""

import argparse
import sys

from agents import detect_available_agents
from config import CONFIG_FILE, load_config, save_config
from config.schema import validate_agent, validate_profile_reference


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

    # config path
    path_parser = config_subparsers.add_parser(
        "path",
        help="Show config file path",
        description="Show configuration file path",
    )
    path_parser.set_defaults(func=run_path)

    # Default to showing help if no subcommand
    parser.set_defaults(func=lambda args: parser.print_help() or 1)


def run_set(args: argparse.Namespace) -> int:
    """Set a configuration value with validation."""
    key = args.key.lower()
    value = args.value
    force = getattr(args, "force", False)

    # Parse key (support dotted notation like "validation.strict")
    if "." in key:
        parts = key.split(".", 1)
        if len(parts) != 2:
            print(f"Error: Invalid key '{key}'. Use format 'section.field' or 'agent'", file=sys.stderr)
            return 1
        section, field = parts
    elif key == "agent":
        # Special case: bare "agent" means "agent.default"
        section, field = "agent", "default"
    else:
        print(f"Error: Invalid key '{key}'. Use format 'section.field' or 'agent'", file=sys.stderr)
        return 1

    # Type coercion based on field
    original_value = value
    if field == "strict":
        value = value.lower() in ("true", "1", "yes", "on")
    elif field == "reference_max_lines":
        try:
            value = int(value)
            if value < 1:
                print(f"Error: '{field}' must be a positive integer", file=sys.stderr)
                return 1
        except ValueError:
            print(f"Error: '{field}' must be an integer", file=sys.stderr)
            return 1

    # Load config
    config_path = getattr(args, "config", None)
    config = load_config(config_path=config_path)

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
                print("\nCreate the profile in ~/.oasr/config.toml first, or use:", file=sys.stderr)
                print(f"  oasr config set --force oasr.default_profile {value}", file=sys.stderr)
                return 1

    # Set the value
    if section not in config:
        config[section] = {}

    config[section][field] = value

    try:
        save_config(config, config_path=config_path)

        # Show confirmation
        if section == "agent" and field == "default":
            # Special handling for agent - check if available
            available = detect_available_agents()
            if value in available:
                print(f"✓ Default agent set to: {value}")
            else:
                print(f"✓ Default agent set to: {value}")
                print(f"  Warning: '{value}' binary not found in PATH. Install it to use this agent.", file=sys.stderr)
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

    if key == "agent":
        agent = config["agent"].get("default")
        if agent:
            print(agent)
        else:
            print("No default agent configured", file=sys.stderr)
            return 1
        return 0
    else:
        print(f"Error: Unsupported config key '{key}'. Only 'agent' is supported.", file=sys.stderr)
        return 1


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

    return 0


def run_path(args: argparse.Namespace) -> int:
    """Show config file path."""
    if hasattr(args, "config") and args.config:
        config_path = args.config
    else:
        config_path = CONFIG_FILE
    print(config_path)
    return 0
