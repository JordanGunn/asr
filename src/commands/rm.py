"""`asr rm` command."""

from __future__ import annotations

import argparse
import glob as globlib
import json
import sys
from fnmatch import fnmatchcase
from pathlib import Path

from registry import load_registry, remove_skill

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


def _match_registry_targets(target: str, entries) -> list:
    """Match a rm target against registry entries.

    Rules:
    - If target looks like a glob, match by name first (fnmatch), then by path.
    - Otherwise match by exact name or exact path.
    """
    target_expanded = str(Path(target).expanduser())
    if _looks_like_glob(target_expanded):
        by_name = [e for e in entries if fnmatchcase(e.name, target_expanded)]
        if by_name:
            return by_name
        return [e for e in entries if fnmatchcase(e.path, target_expanded)]

    return [e for e in entries if e.name == target or e.path == target_expanded]


def register(subparsers) -> None:
    p = subparsers.add_parser("rm", help="Unregister a skill")
    p.add_argument("targets", nargs="+", help="Skill name(s), path(s), or glob pattern(s) to remove")
    p.add_argument("-r", "--recursive", action="store_true", help="Recursively remove all skills under path")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    if args.recursive:
        return _run_recursive(args)

    entries = load_registry()
    removed_names: list[str] = []
    missing: list[str] = []

    for target in args.targets:
        matches = _match_registry_targets(target, entries)
        if not matches:
            missing.append(target)
            continue

        for entry in matches:
            if remove_skill(entry.name):
                removed_names.append(entry.name)

    # Deduplicate while preserving order.
    seen = set()
    removed_names = [n for n in removed_names if not (n in seen or seen.add(n))]

    if args.json:
        print(json.dumps({"removed": len(removed_names), "skills": removed_names, "missing": missing}, indent=2))
    else:
        for name in removed_names:
            print(f"Removed: {name}")
        for m in missing:
            print(f"Not found: {m}", file=sys.stderr)

        if removed_names and not missing:
            print(f"\n{len(removed_names)} skill(s) removed")
        elif removed_names and missing:
            print(f"\n{len(removed_names)} skill(s) removed, {len(missing)} not found")

    return 0 if removed_names and not missing else 1 if missing else 0


def _run_recursive(args: argparse.Namespace) -> int:
    roots = [p.resolve() for p in _expand_path_patterns(args.targets)]
    for root in roots:
        if not root.is_dir():
            print(f"Error: Not a directory: {root}", file=sys.stderr)
            return 2

    entries = load_registry()
    removed_names: list[str] = []

    for root in roots:
        root_str = str(root)
        to_remove = [e for e in entries if e.path.startswith(root_str)]
        for entry in to_remove:
            if remove_skill(entry.name):
                removed_names.append(entry.name)

    # Deduplicate while preserving order.
    seen = set()
    removed_names = [n for n in removed_names if not (n in seen or seen.add(n))]

    if args.json:
        print(json.dumps({"removed": len(removed_names), "skills": removed_names}, indent=2))
    else:
        if not removed_names:
            for root in roots:
                print(f"No registered skills found under {root}")
            return 0
        for name in removed_names:
            print(f"Removed: {name}")
        print(f"\n{len(removed_names)} skill(s) removed")

    return 0
