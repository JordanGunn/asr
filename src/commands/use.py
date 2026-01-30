"""`asr use` command."""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path

from skillcopy import copy_skill
from registry import load_registry


def register(subparsers) -> None:
    p = subparsers.add_parser("use", help="Copy skill(s) to target directory")
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


def _match_skills(patterns: list[str], entry_map: dict) -> tuple[list[str], list[str]]:
    """Match skill names against patterns (exact or glob).
    
    Returns:
        Tuple of (matched_names, unmatched_patterns).
    """
    matched = set()
    unmatched = []
    all_names = list(entry_map.keys())
    
    for pattern in patterns:
        if pattern in entry_map:
            matched.add(pattern)
        elif any(c in pattern for c in "*?["):
            # Glob pattern
            matches = fnmatch.filter(all_names, pattern)
            if matches:
                matched.update(matches)
            else:
                unmatched.append(pattern)
        else:
            unmatched.append(pattern)
    
    return list(matched), unmatched


def run(args: argparse.Namespace) -> int:
    entries = load_registry()
    entry_map = {e.name: e for e in entries}

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    warnings = []

    matched_names, unmatched = _match_skills(args.names, entry_map)
    
    for pattern in unmatched:
        warnings.append(f"No skills matched: {pattern}")

    for name in sorted(matched_names):
        entry = entry_map[name]
        dest = output_dir / name

        try:
            # Unified copy - handles both local and remote
            copy_skill(entry.path, dest, validate=False)
            copied.append({"name": name, "src": entry.path, "dest": str(dest)})
        except Exception as e:
            warnings.append(f"Failed to copy {name}: {e}")

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
