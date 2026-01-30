"""`oasr sync` command - refresh tracked local skills."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from manifest import load_manifest
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
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    """Refresh outdated tracked skills."""
    scan_path = args.path.resolve()

    if not scan_path.exists():
        print(f"Error: Path does not exist: {scan_path}", file=sys.stderr)
        return 1

    # Find all SKILL.md files recursively
    if not args.quiet and not args.json:
        print(f"Scanning {scan_path} for tracked skills...", file=sys.stderr)

    tracked_skills = []
    skill_md_files = list(scan_path.rglob("SKILL.md"))

    for skill_md in skill_md_files:
        skill_dir = skill_md.parent
        metadata = extract_metadata(skill_dir)

        if metadata:
            tracked_skills.append((skill_dir, metadata))

    if not tracked_skills:
        if args.json:
            print(json.dumps({"updated": 0, "skipped": 0, "failed": 0}))
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
    results = []

    if not args.quiet and not args.json:
        print(f"Found {len(tracked_skills)} tracked skill(s)...", file=sys.stderr)

    for skill_dir, metadata in tracked_skills:
        skill_name = skill_dir.name
        tracked_hash = metadata.get("hash")

        # Check if in registry
        if skill_name not in entry_map:
            skipped += 1
            results.append(
                {"name": skill_name, "path": str(skill_dir), "status": "skipped", "message": "Not in registry"}
            )
            if not args.quiet and not args.json:
                print(f"  ? {skill_name}: skipped (not in registry)", file=sys.stderr)
            continue

        entry = entry_map[skill_name]
        manifest = load_manifest(skill_name)

        if not manifest:
            skipped += 1
            results.append({"name": skill_name, "path": str(skill_dir), "status": "skipped", "message": "No manifest"})
            if not args.quiet and not args.json:
                print(f"  ? {skill_name}: skipped (no manifest)", file=sys.stderr)
            continue

        # Check if outdated (compare tracked hash with registry hash)
        if manifest.content_hash == tracked_hash:
            # Already up-to-date
            results.append({"name": skill_name, "path": str(skill_dir), "status": "up-to-date", "message": "Current"})
            if not args.quiet and not args.json:
                print(f"  ✓ {skill_name}: up to date", file=sys.stderr)
            continue

        # Update skill
        try:
            if not args.quiet and not args.json:
                print(f"  ↻ {skill_name}: updating...", file=sys.stderr, flush=True)

            copy_skill(entry.path, skill_dir, validate=False, inject_tracking=True, source_hash=manifest.content_hash)

            updated += 1
            results.append(
                {"name": skill_name, "path": str(skill_dir), "status": "updated", "message": "Refreshed from registry"}
            )
            if not args.quiet and not args.json:
                print(f"  ✓ {skill_name}: updated", file=sys.stderr)
        except Exception as e:
            failed += 1
            results.append({"name": skill_name, "path": str(skill_dir), "status": "failed", "message": str(e)})
            if not args.quiet and not args.json:
                print(f"  ✗ {skill_name}: failed ({e})", file=sys.stderr)

    if args.json:
        print(
            json.dumps(
                {
                    "updated": updated,
                    "skipped": skipped,
                    "failed": failed,
                    "skills": results,
                },
                indent=2,
            )
        )
    else:
        if updated > 0 or skipped > 0 or failed > 0:
            print(f"\n{updated} updated, {skipped} skipped, {failed} failed")
        else:
            print("All tracked skills up to date.")

    return 1 if failed > 0 else 0
