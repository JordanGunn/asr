"""`asr adapter` command."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from adapters import ClaudeAdapter, CodexAdapter, CopilotAdapter, CursorAdapter, WindsurfAdapter
from config import load_config
from registry import load_registry

ADAPTERS = {
    "cursor": CursorAdapter(),
    "windsurf": WindsurfAdapter(),
    "codex": CodexAdapter(),
    "copilot": CopilotAdapter(),
    "claude": ClaudeAdapter(),
}


def register(subparsers) -> None:
    p = subparsers.add_parser("adapter", help="Generate IDE-specific files")
    p.add_argument("--exclude", help="Comma-separated skill names to exclude")
    p.add_argument("--output-dir", type=Path, default=Path("."), help="Output directory")
    p.add_argument("--copy", action="store_true", help="(Deprecated) Skills are always copied now")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.add_argument("--config", type=Path, help="Override config file path")

    adapter_subs = p.add_subparsers(dest="target", help="Target IDE")

    for name in ["cursor", "windsurf", "codex", "copilot", "claude"]:
        adapter_subs.add_parser(name, help=f"Generate {name} files")

    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    entries = load_registry()

    if not entries:
        if args.json:
            print(json.dumps({"generated": 0, "error": "no skills registered"}))
        else:
            print("No skills registered. Use 'asr add <path>' first.")
        return 1

    exclude = set()
    if args.exclude:
        exclude = set(args.exclude.split(","))

    output_dir = args.output_dir

    if args.target:
        targets = [args.target]
    else:
        targets = config["adapter"]["default_targets"]

    total_generated = 0
    total_removed = 0
    results = {}

    for target in targets:
        if target not in ADAPTERS:
            if not args.quiet:
                print(f"Warning: Unknown adapter target: {target}", file=sys.stderr)
            continue

        adapter = ADAPTERS[target]
        # Always copy skills now (--copy flag is deprecated but kept for backward compat)
        generated, removed = adapter.generate_all(entries, output_dir, exclude, copy=True)

        total_generated += len(generated)
        total_removed += len(removed)

        results[target] = {
            "generated": len(generated),
            "removed": len(removed),
            "output_dir": str(adapter.resolve_output_dir(output_dir)),
        }

    if args.json:
        print(
            json.dumps(
                {
                    "total_generated": total_generated,
                    "total_removed": total_removed,
                    "targets": results,
                },
                indent=2,
            )
        )
    else:
        for target, info in results.items():
            print(f"{target}: Generated {info['generated']} file(s) in {info['output_dir']}")
            if info["removed"]:
                print(f"  Removed {info['removed']} stale file(s)")

    return 0
