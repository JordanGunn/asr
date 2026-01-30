"""`asr sync` command."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from config import load_config
from manifest import (
    load_manifest,
    check_manifest,
    sync_manifest,
    save_manifest,
    create_manifest,
)
from registry import load_registry, remove_skill
from validate import validate_skill


def register(subparsers) -> None:
    p = subparsers.add_parser("sync", help="Sync skills from source (using manifests)")
    p.add_argument("names", nargs="*", help="Skill name(s) to sync (default: all)")
    p.add_argument("-d", "--dir", type=Path, dest="output_dir", help="Target directory to copy skills to")
    p.add_argument("--update", action="store_true", help="Update manifests for modified skills")
    p.add_argument("--prune", action="store_true", help="Remove skills with missing sources from registry")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.add_argument("--config", type=Path, help="Override config file path")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    entries = load_registry()
    config = load_config(args.config)
    max_lines = config["validation"]["reference_max_lines"]

    if not entries:
        if args.json:
            print(json.dumps({"synced": 0, "error": "no skills registered"}))
        else:
            print("No skills registered.")
        return 0

    if args.names:
        entry_map = {e.name: e for e in entries}
        entries = [entry_map[n] for n in args.names if n in entry_map]
        missing = [n for n in args.names if n not in entry_map]
        if missing and not args.quiet:
            for n in missing:
                print(f"⚠ Skill not found: {n}", file=sys.stderr)

    # Check for remote skills and show progress header
    from skillcopy.remote import is_remote_source
    remote_count = 0
    for entry in entries:
        manifest = load_manifest(entry.name)
        if manifest and is_remote_source(manifest.source_path):
            remote_count += 1
    
    if remote_count > 0 and not args.quiet and not args.json:
        print(f"Checking {remote_count} remote skill(s)...", file=sys.stderr)

    results = []
    synced = 0
    missing_count = 0
    modified_count = 0
    pruned = []

    for entry in entries:
        manifest = load_manifest(entry.name)

        if manifest is None:
            manifest = create_manifest(
                name=entry.name,
                source_path=Path(entry.path),
                description=entry.description,
            )
            save_manifest(manifest)
            status_info = {"name": entry.name, "status": "created", "message": "Manifest created"}
        else:
            # Show progress for remote skills
            is_remote = is_remote_source(manifest.source_path)
            if is_remote and not args.quiet and not args.json:
                platform = "GitHub" if "github.com" in manifest.source_path else "GitLab" if "gitlab.com" in manifest.source_path else "remote"
                print(f"  ↓ {entry.name} (checking {platform}...)", file=sys.stderr, flush=True)
            
            status = check_manifest(manifest)
            
            if is_remote and not args.quiet and not args.json:
                print(f"  ✓ {entry.name} (checked)", file=sys.stderr)

            if status.status == "missing":
                missing_count += 1
                status_info = status.to_dict()

                if args.prune:
                    remove_skill(entry.name)
                    pruned.append(entry.name)
                    status_info["pruned"] = True
            elif status.status == "modified":
                modified_count += 1
                status_info = status.to_dict()

                if args.update:
                    result = validate_skill(Path(entry.path), reference_max_lines=max_lines)
                    if result.valid:
                        manifest = sync_manifest(manifest)
                        status_info["updated"] = True
                        synced += 1
                    else:
                        status_info["updated"] = False
                        status_info["validation_errors"] = result.errors
            else:
                status_info = status.to_dict()
                synced += 1

        if args.output_dir and status_info.get("status") != "missing":
            src = Path(entry.path)
            dest = args.output_dir.resolve() / entry.name
            if src.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(src, dest)
                status_info["copied_to"] = str(dest)

        results.append(status_info)

    if args.json:
        print(
            json.dumps(
                {
                    "synced": synced,
                    "missing": missing_count,
                    "modified": modified_count,
                    "pruned": pruned,
                    "skills": results,
                },
                indent=2,
            )
        )
    else:
        for r in results:
            status = r.get("status", "unknown")
            name = r.get("name", "?")

            if status == "valid":
                print(f"✓ {name}: up to date")
            elif status == "created":
                print(f"+ {name}: manifest created")
            elif status == "missing":
                if r.get("pruned"):
                    print(f"✗ {name}: source missing (pruned)")
                else:
                    print(f"✗ {name}: source missing")
            elif status == "modified":
                if r.get("updated"):
                    print(f"↻ {name}: updated manifest")
                else:
                    print(f"⚠ {name}: modified (use --update to sync)")

            if r.get("copied_to"):
                print(f"  → {r['copied_to']}")

        if not args.quiet:
            print(f"\n{synced} valid, {modified_count} modified, {missing_count} missing")
            if pruned:
                print(f"Pruned {len(pruned)} skill(s) with missing sources")

    return 0
