"""`asr find` command."""

from __future__ import annotations

import argparse
from pathlib import Path

from discovery import find_skills
from output import error, json_enabled, json_output, json_v2, summary
from registry import SkillEntry, add_skill


def register(subparsers) -> None:
    p = subparsers.add_parser("find", help="Find skills recursively")
    p.add_argument("root", type=Path, help="Root directory to search")
    p.add_argument("--add", action="store_true", dest="add_found", help="Register found skills")
    p.add_argument(
        "--json",
        nargs="?",
        const="v1",
        choices=["v1", "v2"],
        help="Output in JSON format",
    )
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    root = args.root.resolve()

    if not root.is_dir():
        error(f"Not a directory: {root}", hint="Provide a directory path to search")
        return 2

    skills = find_skills(root)

    if json_enabled(args.json):
        data = [{"name": s.name, "description": s.description, "path": str(s.path)} for s in skills]
        payload = data if not json_v2(args.json) else {"skills": data}
        json_output(payload, command="find", v2=json_v2(args.json))
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

        if not json_enabled(args.json) and not args.quiet:
            summary({"registered": added, "updated": len(skills) - added})

    return 0
