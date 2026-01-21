"""`asr use` command."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from registry import load_registry


def register(subparsers) -> None:
    p = subparsers.add_parser("use", help="Copy skill(s) to target directory")
    p.add_argument("names", nargs="+", help="Skill name(s) to copy")
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
    entries = load_registry()
    entry_map = {e.name: e for e in entries}

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    warnings = []

    for name in args.names:
        if name not in entry_map:
            warnings.append(f"Skill not found: {name} (run 'asr validate' or 'asr add')")
            continue

        entry = entry_map[name]
        src = Path(entry.path)

        if not src.exists():
            warnings.append(f"Skill path missing: {name} at {entry.path}")
            continue

        dest = output_dir / name

        if dest.exists():
            shutil.rmtree(dest)

        shutil.copytree(src, dest)
        copied.append({"name": name, "src": str(src), "dest": str(dest)})

    if not args.quiet:
        for w in warnings:
            print(f"⚠ {w}", file=sys.stderr)

    if args.json:
        print(
            json.dumps(
                {
                    "copied": len(copied),
                    "warnings": len(warnings),
                    "skills": copied,
                },
                indent=2,
            )
        )
    else:
        for c in copied:
            print(f"Copied: {c['name']} → {c['dest']}")
        if copied:
            print(f"\n{len(copied)} skill(s) copied to {output_dir}")

    return 1 if warnings and not copied else 0
