"""`asr use` command - DEPRECATED, use `oasr clone` instead."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from commands import clone


def register(subparsers) -> None:
    """Register the deprecated use command."""
    p = subparsers.add_parser(
        "use",
        help="[DEPRECATED] Copy skill(s) - use 'clone' instead",
        description="DEPRECATED: Use 'oasr clone' instead. This command will be removed in v0.5.0.",
    )
    p.add_argument("names", nargs="+", help="Skill name(s) or glob pattern(s) to copy")
    p.add_argument(
        "-d",
        "--dir",
        type=Path,
        default=Path("."),
        dest="output_dir",
        help="Target directory (default: current)",
    )
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    """Execute the deprecated use command (delegates to clone)."""
    # Show deprecation warning unless --quiet or --json
    if not args.quiet and not args.json:
        print(
            "⚠ Warning: 'oasr use' is deprecated. Use 'oasr clone' instead.",
            file=sys.stderr,
        )
        print("  This command will be removed in v0.5.0.", file=sys.stderr)
        print(file=sys.stderr)

    # Delegate to clone command
    return clone.run(args)
