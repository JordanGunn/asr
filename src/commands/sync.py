"""`oasr sync` command - refresh tracked local skills."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from manifest import load_manifest
from output import (
    error,
    json_enabled,
    json_output,
    json_v2,
    progress_counter,
    require_confirmation,
    status_line,
    summary,
)
from skillcopy import copy_skill
from tracking import extract_metadata


def register(subparsers) -> None:
    """Register the sync command."""
    p = subparsers.add_parser("sync", help="Refresh outdated tracked skills from registry")
    p.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Path to scan for tracked skills (default: current directory)",
    )
    p.add_argument("--force", action="store_true", help="Overwrite modified skills (default: skip)")
    p.add_argument("--prune", action="store_true", help="Remove tracked skills not in registry")
    p.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation prompt (requires --prune)",
    )
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
    """Refresh outdated tracked skills."""
    scan_path = args.path.resolve()

    if not scan_path.exists():
        error(f"Path does not exist: {scan_path}", hint="Check the path and try again")
        return 1

    # Find all SKILL.md files recursively
    if not args.quiet and not json_enabled(args.json):
        print(f"Scanning {scan_path} for tracked skills...", file=sys.stderr)

    tracked_skills = []
    skill_md_files = list(scan_path.rglob("SKILL.md"))

    for skill_md in skill_md_files:
        skill_dir = skill_md.parent
        metadata = extract_metadata(skill_dir)

        if metadata:
            tracked_skills.append((skill_dir, metadata))

    if not tracked_skills:
        if json_enabled(args.json):
            json_output({"updated": 0, "skipped": 0, "failed": 0}, command="sync", v2=json_v2(args.json))
        else:
            print("No tracked skills found.")
        return 0

    # Check status and update outdated skills
    from registry import load_registry

    entries = load_registry()
    entry_map = {e.name: e for e in entries}

    updated = 0
    skipped = 0
    failed = 0
    pruned = 0
    results = []
    prune_candidates = []

    if not args.quiet and not json_enabled(args.json):
        print(f"Found {len(tracked_skills)} tracked skill(s)...", file=sys.stderr)

    for index, (skill_dir, metadata) in enumerate(tracked_skills, start=1):
        skill_name = skill_dir.name
        tracked_hash = metadata.get("hash")

        # Check if in registry
        if skill_name not in entry_map:
            skipped += 1
            results.append(
                {"name": skill_name, "path": str(skill_dir), "status": "skipped", "message": "Not in registry"}
            )
            prune_candidates.append(skill_dir)
            if not args.quiet and not json_enabled(args.json):
                status_line("warning", skill_name, "skipped (not in registry)")
            continue

        entry = entry_map[skill_name]
        manifest = load_manifest(skill_name)

        if not manifest:
            skipped += 1
            results.append({"name": skill_name, "path": str(skill_dir), "status": "skipped", "message": "No manifest"})
            if not args.quiet and not json_enabled(args.json):
                status_line("warning", skill_name, "skipped (no manifest)")
            continue

        # Check if outdated (compare tracked hash with registry hash)
        if manifest.content_hash == tracked_hash:
            # Already up-to-date
            results.append({"name": skill_name, "path": str(skill_dir), "status": "up-to-date", "message": "Current"})
            if not args.quiet and not json_enabled(args.json):
                status_line("success", skill_name, "up to date")
            continue

        # Update skill
        try:
            if not args.quiet and not json_enabled(args.json):
                progress_counter(index, len(tracked_skills), f"Updating {skill_name}...")

            copy_skill(entry.path, skill_dir, validate=False, inject_tracking=True, source_hash=manifest.content_hash)

            updated += 1
            results.append(
                {"name": skill_name, "path": str(skill_dir), "status": "updated", "message": "Refreshed from registry"}
            )
            if not args.quiet and not json_enabled(args.json):
                status_line("success", skill_name, "updated")
        except Exception as e:
            failed += 1
            results.append({"name": skill_name, "path": str(skill_dir), "status": "failed", "message": str(e)})
            if not args.quiet and not json_enabled(args.json):
                status_line("error", skill_name, f"failed ({e})")

    if args.prune and prune_candidates:
        if not require_confirmation(
            f"Remove {len(prune_candidates)} tracked skill(s) not in registry?",
            yes_flag=args.yes,
            default=False,
        ):
            if not json_enabled(args.json):
                print("Aborted.")
            return 1

        import shutil

        for skill_dir in prune_candidates:
            try:
                shutil.rmtree(skill_dir)
                pruned += 1
                results.append(
                    {"name": skill_dir.name, "path": str(skill_dir), "status": "pruned", "message": "Removed"}
                )
            except Exception as e:
                failed += 1
                results.append({"name": skill_dir.name, "path": str(skill_dir), "status": "failed", "message": str(e)})
                if not args.quiet and not json_enabled(args.json):
                    status_line("error", skill_dir.name, f"failed ({e})")

    if json_enabled(args.json):
        json_output(
            {
                "updated": updated,
                "skipped": skipped,
                "failed": failed,
                "pruned": pruned,
                "skills": results,
            },
            command="sync",
            v2=json_v2(args.json),
        )
    else:
        if updated > 0 or skipped > 0 or failed > 0 or pruned > 0:
            summary({"updated": updated, "skipped": skipped, "pruned": pruned, "failed": failed})
        else:
            print("All tracked skills up to date.")

    return 1 if failed > 0 else 0
