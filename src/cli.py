"""CLI entry point (argparse wiring + dispatch).

Command implementations live under `src/commands/`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from commands import adapter, clean, diff, find, registry, sync, update, use, validate
from commands import help as help_cmd

__version__ = "0.3.4"


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except Exception as e:
        if args.json if hasattr(args, "json") else False:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 3


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="oasr",
        description="Open Agent Skills Registry - Manage agent skills across IDE integrations.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Override config file path",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress info and warnings",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # New taxonomy (v0.3.0)
    registry.register(subparsers)  # Registry operations (add, rm, sync, list)
    diff.register(subparsers)  # Show tracked skill status
    sync.register(subparsers)  # Refresh tracked skills

    # Unchanged commands
    use.register(subparsers)
    find.register(subparsers)
    validate.register(subparsers)
    clean.register(subparsers)
    adapter.register(subparsers)
    update.register(subparsers)

    # Import and register info command
    from commands import info as info_cmd

    info_cmd.register(subparsers)

    help_cmd.register(subparsers, parser)

    return parser


if __name__ == "__main__":
    raise SystemExit(main())
