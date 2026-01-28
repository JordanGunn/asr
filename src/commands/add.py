"""`asr add` command."""

from __future__ import annotations

import argparse
import glob as globlib
import json
import sys
from pathlib import Path

from config import load_config
from discovery import find_skills, discover_single
from registry import SkillEntry, add_skill
from validate import validate_skill

_GLOB_CHARS = set("*?[")


def _looks_like_glob(value: str) -> bool:
    return any(ch in value for ch in _GLOB_CHARS)


def _expand_path_patterns(patterns: list[str]) -> list[Path]:
    expanded: list[Path] = []
    for raw in patterns:
        pat = str(Path(raw).expanduser())
        if _looks_like_glob(pat):
            matches = globlib.glob(pat, recursive=True)
            expanded.extend(Path(m) for m in matches)
        else:
            expanded.append(Path(pat))
    return expanded


def _print_validation_result(result) -> None:
    print(f"{result.name}")
    if result.valid and not result.warnings:
        print("  ✓ Valid")
    else:
        for msg in result.all_messages:
            print(f"  {msg}")


def register(subparsers) -> None:
    p = subparsers.add_parser("add", help="Register a skill")
    p.add_argument(
        "paths",
        nargs="+",
        help="Path(s) (or glob pattern(s)) to skill dir(s) (or root(s) for recursive)",
    )
    p.add_argument("-r", "--recursive", action="store_true", help="Recursively add all valid skills from path")
    p.add_argument("--strict", action="store_true", help="Fail if validation has warnings")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.add_argument("--config", type=Path, help="Override config file path")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    max_lines = config["validation"]["reference_max_lines"]

    expanded = [p.resolve() for p in _expand_path_patterns(args.paths)]
    if not expanded:
        if args.json:
            print(json.dumps({"added": 0, "skipped": 0, "skills": [], "error": "no paths matched"}))
        else:
            print("No paths matched.", file=sys.stderr)
        return 2

    if args.recursive:
        exit_code = 0
        for root in expanded:
            code = _run_recursive(args, root, max_lines)
            if code != 0:
                exit_code = code
        return exit_code

    results: list[dict] = []
    added_count = 0
    skipped_count = 0
    exit_code = 0

    for path in expanded:
        if not path.exists():
            skipped_count += 1
            results.append({"path": str(path), "added": False, "reason": "path missing"})
            exit_code = 1
            if not args.quiet and not args.json:
                print(f"Not found: {path}", file=sys.stderr)
            continue

        result = validate_skill(path, reference_max_lines=max_lines)
        if not args.quiet and not args.json:
            _print_validation_result(result)
            print()

        if not result.valid:
            skipped_count += 1
            results.append({"path": str(path), "added": False, "reason": "validation errors"})
            exit_code = 1
            continue

        if args.strict and result.warnings:
            skipped_count += 1
            results.append({"path": str(path), "added": False, "reason": "validation warnings (strict mode)"})
            exit_code = 1
            continue

        discovered = discover_single(path)
        if not discovered:
            skipped_count += 1
            results.append({"path": str(path), "added": False, "reason": "could not discover skill info"})
            exit_code = 3
            continue

        entry = SkillEntry(
            path=str(discovered.path),
            name=discovered.name,
            description=discovered.description,
        )

        is_new = add_skill(entry)
        added_count += 1
        results.append({"name": entry.name, "path": entry.path, "added": True, "new": is_new})

        if not args.quiet and not args.json:
            action = "Added" if is_new else "Updated"
            print(f"{action} skill: {entry.name}")

    if args.json:
        print(json.dumps({"added": added_count, "skipped": skipped_count, "skills": results}, indent=2))

    return exit_code


def _run_recursive(args: argparse.Namespace, root: Path, max_lines: int) -> int:
    if not root.is_dir():
        print(f"Error: Not a directory: {root}", file=sys.stderr)
        return 2

    skills = find_skills(root)
    if not skills:
        if args.json:
            print(json.dumps({"added": 0, "skipped": 0, "skills": []}))
        else:
            print(f"No skills found under {root}")
        return 0

    added_count = 0
    skipped_count = 0
    results = []

    for s in skills:
        result = validate_skill(s.path, reference_max_lines=max_lines)

        if not result.valid:
            skipped_count += 1
            if not args.quiet:
                print(f"⚠ Skipping {s.name}: validation errors", file=sys.stderr)
            results.append({"name": s.name, "added": False, "reason": "validation errors"})
            continue

        if args.strict and result.warnings:
            skipped_count += 1
            if not args.quiet:
                print(f"⚠ Skipping {s.name}: validation warnings (strict)", file=sys.stderr)
            results.append({"name": s.name, "added": False, "reason": "validation warnings"})
            continue

        entry = SkillEntry(path=str(s.path), name=s.name, description=s.description)
        is_new = add_skill(entry)
        added_count += 1

        if not args.quiet and not args.json:
            action = "Added" if is_new else "Updated"
            print(f"{action}: {s.name}")

        results.append({"name": s.name, "added": True, "new": is_new})

    if args.json:
        print(json.dumps({"added": added_count, "skipped": skipped_count, "skills": results}, indent=2))
    elif not args.quiet:
        print(f"\n{added_count} skill(s) added, {skipped_count} skipped")

    return 0
