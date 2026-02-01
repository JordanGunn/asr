"""Config command - manage OASR configuration."""

import argparse
import sys

from agents import detect_available_agents, get_all_agent_names
from config import CONFIG_FILE, load_config, save_config


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
    """Set a configuration value."""
    key = args.key.lower()
    value = args.value

    # Only support agent for now
    if key == "agent":
        # Validate agent name
        valid_agents = get_all_agent_names()
        if value not in valid_agents:
            print(
                f"Error: Invalid agent '{value}'. Must be one of: {', '.join(valid_agents)}",
                file=sys.stderr,
            )
            return 1

        # Load config, update, save
        config = load_config(args.config if hasattr(args, "config") else None)
        config["agent"]["default"] = value
        save_config(config, args.config if hasattr(args, "config") else None)

        # Show available vs configured
        available = detect_available_agents()
        if value in available:
            print(f"✓ Default agent set to: {value}")
        else:
            print(f"✓ Default agent set to: {value}")
            print(
                f"  Warning: '{value}' binary not found in PATH. Install it to use this agent.",
                file=sys.stderr,
            )

        return 0
    else:
        print(f"Error: Unsupported config key '{key}'. Only 'agent' is supported.", file=sys.stderr)
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
