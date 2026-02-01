"""`asr clean` command - DEPRECATED, use `oasr registry prune` instead."""

from __future__ import annotations

import argparse
import sys


def register(subparsers) -> None:
    p = subparsers.add_parser(
        "clean",
        help="(Deprecated) Clean up corrupted/missing skills - use 'oasr registry prune'",
    )
    p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--dry-run", action="store_true", help="Show what would be cleaned without doing it")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    """Delegate to registry prune with deprecation warning."""
    # Show deprecation warning unless --json or --quiet
    if not args.json:
        print("⚠ Warning: 'oasr clean' is deprecated. Use 'oasr registry prune' instead.", file=sys.stderr)
        print("   This command will be removed in v0.6.0.\n", file=sys.stderr)

    # Delegate to registry prune
    from commands.registry import run_prune

    return run_prune(args)
