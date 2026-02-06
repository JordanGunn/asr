"""`asr help` command."""

from __future__ import annotations

import argparse

COMMAND_HELP = {
    "registry": {
        "examples": [
            ("List registered skills", "oasr registry list"),
            ("Add a skill", "oasr registry add ./my-skill"),
            ("Sync remote skills", "oasr registry sync"),
        ]
    },
    "diff": {
        "examples": [
            ("Check current directory", "oasr diff"),
            ("Check a project path", "oasr diff ./project"),
        ]
    },
    "sync": {
        "examples": [
            ("Sync current directory", "oasr sync"),
            ("Force overwrite", "oasr sync --force"),
            ("Prune unregistered skills", "oasr sync --prune"),
        ]
    },
    "exec": {
        "examples": [
            ("Run with inline prompt", "oasr exec my-skill -p 'do something'"),
            ("Use a profile", "oasr exec my-skill --profile dev"),
        ]
    },
    "config": {
        "examples": [
            ("List config", "oasr config list"),
            ("Set agent", "oasr config set agent codex"),
        ]
    },
    "profile": {
        "examples": [
            ("List profiles", "oasr profile list"),
            ("Set default profile", "oasr profile dev"),
            ("Create a new profile", "oasr profile new my-profile"),
            ("Edit active profile", "oasr profile edit"),
        ]
    },
    "clone": {
        "examples": [
            ("Clone to a directory", "oasr clone git-commit -d ./skills"),
            ("Clone a pattern", "oasr clone git-* -d ./skills"),
        ]
    },
    "adapter": {
        "examples": [
            ("Generate adapters", "oasr adapter --output-dir ./project"),
            ("Generate for Copilot", "oasr adapter copilot --output-dir ./project"),
        ]
    },
    "update": {
        "examples": [
            ("Check for updates", "oasr update --check"),
            ("Update immediately", "oasr update -y"),
        ]
    },
    "completion": {
        "examples": [
            ("Install for current shell", "oasr completion install"),
            ("Dry-run install", "oasr completion bash --install --dry-run"),
        ]
    },
    "info": {
        "examples": [
            ("Show skill info", "oasr info git-commit"),
            ("Include files", "oasr info git-commit --files"),
        ]
    },
    "find": {
        "examples": [
            ("Find skills", "oasr find ./skills"),
            ("Find and add", "oasr find ./skills --add"),
        ]
    },
    "validate": {
        "examples": [
            ("Validate a skill", "oasr validate ./my-skill"),
            ("Validate all skills", "oasr validate --all"),
        ]
    },
    "status": {
        "examples": [
            ("Check registry status", "oasr status"),
            ("Check specific skills", "oasr status git-commit"),
        ]
    },
    "about": {
        "examples": [
            ("Show version and credits", "oasr about"),
        ]
    },
    "help": {
        "examples": [
            ("Show general help", "oasr help"),
            ("Help for a command", "oasr help exec"),
        ]
    },
}


def _print_examples(command: str) -> None:
    info = COMMAND_HELP.get(command, {})
    examples = info.get("examples", [])
    if not examples:
        return
    print("\nExamples:")
    for desc, example in examples:
        print(f"  # {desc}")
        print(f"  $ {example}")


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
        _print_examples(args.command)
        return 0
    else:
        print(f"Unknown command: {args.command}")
        print(f"\nAvailable commands: {', '.join(sorted(subparsers_action.choices.keys()))}")
        return 1
