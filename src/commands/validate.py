"""`asr validate` command."""

from __future__ import annotations

import argparse
from pathlib import Path

from config import load_config
from output import error, json_enabled, json_output, json_v2, progress_counter, summary
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
    p.add_argument(
        "--json",
        nargs="?",
        const="v1",
        choices=["v1", "v2"],
        help="Output in JSON format",
    )
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.add_argument("--config", type=Path, help="Override config file path")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    max_lines = config["validation"]["reference_max_lines"]

    if args.validate_all:
        entries = load_registry()
        if not entries:
            if json_enabled(args.json):
                json_output([], command="validate", v2=json_v2(args.json))
            else:
                print("No skills registered.")
            return 0

        results = validate_all(entries, reference_max_lines=max_lines)
    elif args.path:
        result = validate_skill(args.path.resolve(), reference_max_lines=max_lines)
        results = [result]
    else:
        error("Specify a path or use --all", hint="Try: oasr validate ./my-skill or oasr validate --all")
        return 2

    if json_enabled(args.json):
        payload = [r.to_dict() for r in results]
        if json_v2(args.json):
            payload = {"results": payload}
        json_output(payload, command="validate", v2=json_v2(args.json))
    else:
        for index, result in enumerate(results, start=1):
            progress_counter(index, len(results), f"Validating {result.name}...")
            _print_validation_result(result)
            print()

    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)

    if not json_enabled(args.json) and not args.quiet:
        summary(
            {
                "validated": len(results),
                "errors": total_errors,
                "warnings": total_warnings,
            }
        )

    if total_errors > 0:
        return 1
    if args.strict and total_warnings > 0:
        return 1

    return 0
