"""`asr status` command."""

from __future__ import annotations

import argparse

from manifest import check_manifest, load_manifest
from output import json_enabled, json_output, json_v2, progress_counter, status_line, summary
from registry import load_registry


def register(subparsers) -> None:
    p = subparsers.add_parser("status", help="Show skill manifest status")
    p.add_argument("names", nargs="*", help="Skill name(s) to check (default: all)")
    p.add_argument(
        "--json",
        nargs="?",
        const="v1",
        choices=["v1", "v2"],
        help="Output in JSON format",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    entries = load_registry()

    if not entries:
        if json_enabled(args.json):
            json_output([], command="status", v2=json_v2(args.json))
        else:
            print("No skills registered.")
        return 0

    if args.names:
        entry_map = {e.name: e for e in entries}
        entries = [entry_map[n] for n in args.names if n in entry_map]

    # Check for remote skills and show progress header
    from skillcopy.remote import is_remote_source

    remote_count = 0
    for entry in entries:
        manifest = load_manifest(entry.name)
        if manifest and is_remote_source(manifest.source_path):
            remote_count += 1

    if remote_count > 0 and not json_enabled(args.json):
        import sys

        print(f"Checking {remote_count} remote skill(s)...", file=sys.stderr)

    results = []

    for index, entry in enumerate(entries, start=1):
        manifest = load_manifest(entry.name)

        if manifest is None:
            status_info = {
                "name": entry.name,
                "status": "untracked",
                "source_path": entry.path,
                "message": "No manifest (run 'asr sync' to create)",
            }
        else:
            # Show progress for remote skills
            is_remote = is_remote_source(manifest.source_path)
            if is_remote and not json_enabled(args.json):
                import sys

                platform = (
                    "GitHub"
                    if "github.com" in manifest.source_path
                    else "GitLab"
                    if "gitlab.com" in manifest.source_path
                    else "remote"
                )
                progress_counter(index, len(entries), f"Checking {entry.name} ({platform})...")

            status = check_manifest(manifest)
            status_info = status.to_dict()

            if is_remote and not json_enabled(args.json):
                import sys

                print(f"  ✓ {entry.name} (checked)", file=sys.stderr)

        results.append(status_info)

    if json_enabled(args.json):
        json_output(results if not json_v2(args.json) else {"skills": results}, command="status", v2=json_v2(args.json))
    else:
        for r in results:
            status = r.get("status", "unknown")
            name = r.get("name", "?")

            if status == "valid":
                status_line("success", name)
            elif status == "untracked":
                status_line("warning", name, "untracked")
            elif status == "missing":
                status_line("error", name, "source missing")
            elif status == "modified":
                status_line("warning", name, "modified")
                if r.get("changed_files"):
                    for f in r["changed_files"][:5]:
                        print(f"    ~ {f}")
                    if len(r["changed_files"]) > 5:
                        print(f"    ... and {len(r['changed_files']) - 5} more")
                if r.get("added_files"):
                    for f in r["added_files"][:3]:
                        print(f"    + {f}")
                if r.get("removed_files"):
                    for f in r["removed_files"][:3]:
                        print(f"    - {f}")

    valid = sum(1 for r in results if r.get("status") == "valid")
    modified = sum(1 for r in results if r.get("status") == "modified")
    missing = sum(1 for r in results if r.get("status") == "missing")
    untracked = sum(1 for r in results if r.get("status") == "untracked")

    if not json_enabled(args.json):
        summary({"valid": valid, "modified": modified, "missing": missing, "untracked": untracked})

    return 0
