"""`asr clean` command."""

from __future__ import annotations

import argparse
import json

from manifest import check_manifest, delete_manifest, list_manifests, load_manifest
from registry import load_registry, remove_skill


def register(subparsers) -> None:
    p = subparsers.add_parser("clean", help="Clean up corrupted/missing skills and orphaned artifacts")
    p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--dry-run", action="store_true", help="Show what would be cleaned without doing it")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    entries = load_registry()
    registered_names = {e.name for e in entries}
    manifest_names = set(list_manifests())

    to_remove_skills = []
    to_remove_manifests = []

    # Check for remote skills and show progress header
    import sys

    from skillcopy.remote import is_remote_source

    remote_count = 0
    for entry in entries:
        manifest = load_manifest(entry.name)
        if manifest and is_remote_source(manifest.source_path):
            remote_count += 1

    if remote_count > 0 and not args.json:
        print(f"Checking {remote_count} remote skill(s)...", file=sys.stderr)

    for entry in entries:
        manifest = load_manifest(entry.name)
        if manifest:
            # Show progress for remote skills
            is_remote = is_remote_source(manifest.source_path)
            if is_remote and not args.json:
                platform = (
                    "GitHub"
                    if "github.com" in manifest.source_path
                    else "GitLab"
                    if "gitlab.com" in manifest.source_path
                    else "remote"
                )
                print(f"  ↓ {entry.name} (checking {platform}...)", file=sys.stderr, flush=True)

            status = check_manifest(manifest)

            if is_remote and not args.json:
                print(f"  ✓ {entry.name} (checked)", file=sys.stderr)

            if status.status == "missing":
                to_remove_skills.append(
                    {
                        "name": entry.name,
                        "reason": "source missing",
                        "path": entry.path,
                    }
                )

    orphaned = manifest_names - registered_names
    for name in orphaned:
        to_remove_manifests.append(
            {
                "name": name,
                "reason": "orphaned manifest (not in registry)",
            }
        )

    if not to_remove_skills and not to_remove_manifests:
        if args.json:
            print(json.dumps({"cleaned": 0, "message": "nothing to clean"}))
        else:
            print("Nothing to clean.")
        return 0

    if args.json:
        result = {
            "skills_to_remove": to_remove_skills,
            "manifests_to_remove": to_remove_manifests,
            "dry_run": args.dry_run,
        }
        if not args.dry_run and not args.yes:
            result["requires_confirmation"] = True
        print(json.dumps(result, indent=2))
        if args.dry_run:
            return 0
    else:
        print("The following will be cleaned:\n")

        if to_remove_skills:
            print("Skills with missing sources:")
            for s in to_remove_skills:
                print(f"  ✗ {s['name']} ({s['path']})")

        if to_remove_manifests:
            print("\nOrphaned manifests:")
            for m in to_remove_manifests:
                print(f"  ✗ {m['name']}")

        print()

        if args.dry_run:
            print("(dry run - no changes made)")
            return 0

    if not args.yes and not args.json:
        try:
            response = input("Proceed with cleanup? [y/N] ").strip().lower()
            if response not in ("y", "yes"):
                print("Aborted.")
                return 1
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return 1

    removed_skills = []
    removed_manifests = []

    for s in to_remove_skills:
        remove_skill(s["name"])
        removed_skills.append(s["name"])

    for m in to_remove_manifests:
        delete_manifest(m["name"])
        removed_manifests.append(m["name"])

    if args.json:
        print(
            json.dumps(
                {
                    "removed_skills": removed_skills,
                    "removed_manifests": removed_manifests,
                },
                indent=2,
            )
        )
    else:
        for name in removed_skills:
            print(f"Removed skill: {name}")
        for name in removed_manifests:
            print(f"Removed manifest: {name}")
        print(f"\nCleaned {len(removed_skills)} skill(s), {len(removed_manifests)} manifest(s)")

    return 0
