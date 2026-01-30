"""`asr help` command."""

from __future__ import annotations

import argparse


def register(subparsers, parser_ref: argparse.ArgumentParser) -> None:
    """Register the help subcommand.

    Args:
        subparsers: The subparsers object to add to.
        parser_ref: Reference to the main parser for displaying help.
    """
    p = subparsers.add_parser(
        "help",
        help="Show help for a command",
        add_help=False,
    )
    p.add_argument(
        "command",
        nargs="?",
        help="Command to show help for",
    )
    p.set_defaults(func=lambda args: run(args, parser_ref))


def run(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    """Show help for the specified command or general help."""
    if not args.command:
        parser.print_help()
        return 0

    # Find the subparser for the given command
    subparsers_action = None
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            subparsers_action = action
            break

    if subparsers_action is None:
        print("Error: No commands available")
        return 1

    if args.command in subparsers_action.choices:
        subparsers_action.choices[args.command].print_help()
        return 0
    else:
        print(f"Unknown command: {args.command}")
        print(f"\nAvailable commands: {', '.join(sorted(subparsers_action.choices.keys()))}")
        return 1
