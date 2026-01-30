"""`asr list` command."""

from __future__ import annotations

import argparse
import json
import os
import textwrap
from shutil import get_terminal_size

from registry import load_registry


def register(subparsers) -> None:
    p = subparsers.add_parser("list", help="List registered skills")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--verbose", "-v", action="store_true", help="Show full paths")
    p.set_defaults(func=run)


def _shorten_path(path: str, max_len: int = 40) -> str:
    """Shorten a path for display, using ~ for home directory."""
    home = os.path.expanduser("~")
    if path.startswith(home):
        path = "~" + path[len(home) :]

    if len(path) <= max_len:
        return path

    # Truncate middle of path
    parts = path.split(os.sep)
    if len(parts) <= 2:
        return path[: max_len - 3] + "..."

    # Keep first and last parts, truncate middle
    result = parts[0] + os.sep + "..." + os.sep + parts[-1]
    if len(result) <= max_len:
        # Try to add more parts from the end
        for i in range(len(parts) - 2, 0, -1):
            candidate = parts[0] + os.sep + "..." + os.sep.join(parts[i:])
            if len(candidate) <= max_len:
                result = candidate
            else:
                break
    return result


def _wrap_description(desc: str, width: int, indent: int = 3) -> str:
    """Wrap description text with proper indentation."""
    if not desc:
        return ""
    prefix = " " * indent
    wrapped = textwrap.fill(
        desc.strip(),
        width=max(20, width - indent),
        initial_indent=prefix,
        subsequent_indent=prefix,
    )
    return wrapped


def run(args: argparse.Namespace) -> int:
    entries = load_registry()

    if not entries:
        if args.json:
            print("[]")
        else:
            print("No skills registered. Use 'asr add <path>' to register a skill.")
        return 0

    if args.json:
        data = [{"name": e.name, "description": e.description, "path": e.path} for e in entries]
        print(json.dumps(data, indent=2))
        return 0

    width = min(100, max(60, get_terminal_size((80, 20)).columns))
    verbose = getattr(args, "verbose", False)

    # Header
    print(f"\n  REGISTERED SKILLS ({len(entries)})\n")

    # Calculate max name length for alignment
    max_name = max(len(e.name) for e in entries)
    path_width = width - max_name - 10  # Account for formatting

    for e in sorted(entries, key=lambda x: x.name):
        name = e.name

        if verbose:
            path_display = e.path
        else:
            path_display = _shorten_path(e.path, max(20, path_width))

        # Skill header with box drawing
        print(f"  ┌─ {name}")
        print(f"  │  {path_display}")

        desc = (e.description or "").strip()
        if desc:
            # Truncate description to one line if too long
            max_desc = width - 6
            if len(desc) > max_desc:
                desc = desc[: max_desc - 3] + "..."
            print(f"  └─ {desc}")
        else:
            print("  └─ (no description)")
        print()

    return 0
