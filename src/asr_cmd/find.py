"""`asr find` command."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from discovery import find_skills
from registry import SkillEntry, add_skill


def register(subparsers) -> None:
    p = subparsers.add_parser("find", help="Find skills recursively")
    p.add_argument("root", type=Path, help="Root directory to search")
    p.add_argument("--add", action="store_true", dest="add_found", help="Register found skills")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    root = args.root.resolve()

    if not root.is_dir():
        print(f"Error: Not a directory: {root}", file=sys.stderr)
        return 2

    skills = find_skills(root)

    if args.json:
        data = [{"name": s.name, "description": s.description, "path": str(s.path)} for s in skills]
        print(json.dumps(data, indent=2))
    else:
        if not skills:
            print(f"No skills found under {root}")
        else:
            for s in skills:
                print(f"{s.name:<30}  {s.path}")

    if args.add_found and skills:
        added = 0
        for s in skills:
            entry = SkillEntry(
                path=str(s.path),
                name=s.name,
                description=s.description,
            )
            if add_skill(entry):
                added += 1

        if not args.json and not args.quiet:
            print(f"\nRegistered {added} new skill(s), {len(skills) - added} updated.")

    return 0
