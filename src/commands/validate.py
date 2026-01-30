"""`asr validate` command."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from config import load_config
from registry import load_registry
from validate import validate_all, validate_skill


def _print_validation_result(result) -> None:
    print(f"{result.name}")
    if result.valid and not result.warnings:
        print("  ✓ Valid")
    else:
        for msg in result.all_messages:
            print(f"  {msg}")


def register(subparsers) -> None:
    p = subparsers.add_parser("validate", help="Validate skills")
    p.add_argument("path", type=Path, nargs="?", help="Path to skill directory")
    p.add_argument("--all", action="store_true", dest="validate_all", help="Validate all registered skills")
    p.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.add_argument("--config", type=Path, help="Override config file path")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    max_lines = config["validation"]["reference_max_lines"]

    if args.validate_all:
        entries = load_registry()
        if not entries:
            if args.json:
                print("[]")
            else:
                print("No skills registered.")
            return 0

        results = validate_all(entries, reference_max_lines=max_lines)
    elif args.path:
        result = validate_skill(args.path.resolve(), reference_max_lines=max_lines)
        results = [result]
    else:
        print("Error: Specify a path or use --all", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        for result in results:
            _print_validation_result(result)
            print()

    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)

    if not args.json and not args.quiet:
        print(f"{len(results)} skill(s) validated: {total_errors} error(s), {total_warnings} warning(s)")

    if total_errors > 0:
        return 1
    if args.strict and total_warnings > 0:
        return 1

    return 0
