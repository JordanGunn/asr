"""`asr list` command."""

from __future__ import annotations

import argparse
import json
import textwrap
from shutil import get_terminal_size

from registry import load_registry


def register(subparsers) -> None:
    p = subparsers.add_parser("list", help="List registered skills")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.set_defaults(func=run)


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

    width = max(60, get_terminal_size((100, 20)).columns)
    for e in entries:
        print(f"{e.name} ({e.path})")
        desc = (e.description or "").strip()
        if desc:
            print(
                textwrap.fill(
                    desc,
                    width=max(20, width - 2),
                    initial_indent="  ",
                    subsequent_indent="  ",
                )
            )
        print()

    return 0
