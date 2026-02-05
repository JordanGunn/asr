"""`oasr registry` command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from manifest import (
    check_manifest,
    create_manifest,
    load_manifest,
    save_manifest,
    sync_manifest,
)
from output import (
    json_enabled,
    json_output,
    json_v2,
    progress_counter,
    require_confirmation,
    status_line,
    summary,
    warn,
)
from registry import load_registry, remove_skill
from skillcopy.remote import is_remote_source


def register(subparsers) -> None:
    """Register the registry command and subcommands."""
    p = subparsers.add_parser("registry", help="Manage skill registry (validate, add, remove, sync)")

    # Subcommands
    registry_subparsers = p.add_subparsers(dest="registry_command", help="Registry operation")

    # registry (default - validate)
    p.add_argument("-v", "--verbose", action="store_true", help="Show detailed per-skill status")
    p.add_argument(
        "--json",
        nargs="?",
        const="v1",
        choices=["v1", "v2"],
        help="Output in JSON format",
    )
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.add_argument("--config", type=Path, help="Override config file path")
    p.set_defaults(func=run_validate)

    # registry list
    list_p = registry_subparsers.add_parser("list", help="List all registered skills")
    list_p.add_argument(
        "--no-unicode",
        action="store_true",
        help="Disable unicode symbols in output",
    )
    list_p.add_argument(
        "--json",
        nargs="?",
        const="v1",
        choices=["v1", "v2"],
        help="Output in JSON format",
    )
    list_p.set_defaults(func=run_list)

    # registry add
    add_p = registry_subparsers.add_parser("add", help="Add skill(s) to registry")
    add_p.add_argument("paths", nargs="+", help="Path(s) or URL(s) to skill directories")
    add_p.add_argument("-r", "--recursive", action="store_true", help="Recursively discover skills")
    add_p.add_argument("--strict", action="store_true", help="Fail on validation warnings")
    add_p.add_argument(
        "--json",
        nargs="?",
        const="v1",
        choices=["v1", "v2"],
        help="Output in JSON format",
    )
    add_p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    add_p.add_argument("--config", type=Path, help="Override config file path")
    add_p.set_defaults(func=run_add)

    # registry rm
    rm_p = registry_subparsers.add_parser("rm", help="Remove skill(s) from registry")
    rm_p.add_argument("targets", nargs="+", help="Skill name(s), path(s), or glob pattern(s) to remove")
    rm_p.add_argument("-r", "--recursive", action="store_true", help="Recursively remove skills")
    rm_p.add_argument(
        "--json",
        nargs="?",
        const="v1",
        choices=["v1", "v2"],
        help="Output in JSON format",
    )
    rm_p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    rm_p.set_defaults(func=run_rm)

    # registry sync
    sync_p = registry_subparsers.add_parser("sync", help="Sync registry with remote sources")
    sync_p.add_argument("names", nargs="*", help="Skill name(s) to sync (default: all)")
    sync_p.add_argument("--prune", action="store_true", help="Remove skills with missing sources")
    sync_p.add_argument(
        "--json",
        nargs="?",
        const="v1",
        choices=["v1", "v2"],
        help="Output in JSON format",
    )
    sync_p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    sync_p.add_argument("--config", type=Path, help="Override config file path")
    sync_p.set_defaults(func=run_sync)

    # registry prune
    prune_p = registry_subparsers.add_parser("prune", help="Clean up corrupted/missing skills and orphaned artifacts")
    prune_p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    prune_p.add_argument(
        "--json",
        nargs="?",
        const="v1",
        choices=["v1", "v2"],
        help="Output in JSON format",
    )
    prune_p.add_argument("--dry-run", action="store_true", help="Show what would be cleaned without doing it")
    prune_p.set_defaults(func=run_prune)


def run_validate(args: argparse.Namespace) -> int:
    """Validate registry manifests (default oasr registry behavior)."""
    entries = load_registry()
    json_mode_v2 = json_v2(args.json)

    if not entries:
        if json_enabled(args.json):
            json_output({"valid": 0, "modified": 0, "missing": 0}, command="registry", v2=json_mode_v2)
        else:
            print("No skills registered.")
        return 0

    # Check for remote skills
    remote_count = sum(
        1 for entry in entries if (manifest := load_manifest(entry.name)) and is_remote_source(manifest.source_path)
    )

    if remote_count > 0 and not args.quiet and not json_enabled(args.json):
        print(f"Checking {remote_count} remote skill(s)...", file=sys.stderr)

    valid_count = 0
    modified_count = 0
    missing_count = 0
    results = []

    for index, entry in enumerate(entries, start=1):
        manifest = load_manifest(entry.name)

        if manifest is None:
            # Create missing manifest
            manifest = create_manifest(
                name=entry.name,
                source_path=Path(entry.path),
                description=entry.description,
            )
            save_manifest(manifest)
            valid_count += 1
            status_info = {"name": entry.name, "status": "valid", "message": "Manifest created"}
        else:
            # Show progress for remote skills
            is_remote = is_remote_source(manifest.source_path)
            if is_remote and not args.quiet and not json_enabled(args.json):
                platform = (
                    "GitHub"
                    if "github.com" in manifest.source_path
                    else "GitLab"
                    if "gitlab.com" in manifest.source_path
                    else "remote"
                )
                progress_counter(index, len(entries), f"Checking {entry.name} ({platform})...")

            status = check_manifest(manifest)

            if is_remote and not args.quiet and not json_enabled(args.json):
                status_line("success", entry.name, "checked")

            if status.status == "valid":
                valid_count += 1
            elif status.status == "modified":
                modified_count += 1
            elif status.status == "missing":
                missing_count += 1

            status_info = status.to_dict()

        results.append(status_info)

    if json_enabled(args.json):
        json_output(
            {
                "valid": valid_count,
                "modified": modified_count,
                "missing": missing_count,
                "results": results if args.verbose else None,
            },
            command="registry",
            v2=json_mode_v2,
        )
    elif args.verbose:
        # Detailed output (like old oasr status)
        for result in results:
            status_symbol = "✓" if result["status"] == "valid" else "⚠" if result["status"] == "modified" else "✗"
            print(f"{status_symbol} {result['name']}: {result['status']}")
            if result.get("message"):
                print(f"  {result['message']}")
    else:
        # Summary output (like old oasr sync)
        for result in results:
            if result["status"] == "valid":
                print(f"✓ {result['name']}: up to date")
            elif result["status"] == "modified":
                print(f"⚠ {result['name']}: modified")
            elif result["status"] == "missing":
                print(f"✗ {result['name']}: missing")

        summary({"valid": valid_count, "modified": modified_count, "missing": missing_count})

    return 1 if missing_count > 0 else 0


def run_list(args: argparse.Namespace) -> int:
    """List all registered skills (oasr registry list)."""
    from commands.list import run as list_run

    return list_run(args)


def run_add(args: argparse.Namespace) -> int:
    """Add skills to registry (oasr registry add)."""
    from commands.add import run as add_run

    return add_run(args)


def run_rm(args: argparse.Namespace) -> int:
    """Remove skills from registry (oasr registry rm)."""
    from commands.rm import run as rm_run

    return rm_run(args)


def run_sync(args: argparse.Namespace) -> int:
    """Sync registry with remotes (oasr registry sync)."""
    entries = load_registry()
    json_mode_v2 = json_v2(args.json)

    if not entries:
        if json_enabled(args.json):
            json_output({"synced": 0, "error": "no skills registered"}, command="registry", v2=json_mode_v2)
        else:
            print("No skills registered.")
        return 0

    # Filter by names if provided
    if args.names:
        entry_map = {e.name: e for e in entries}
        entries = [entry_map[n] for n in args.names if n in entry_map]
        missing = [n for n in args.names if n not in entry_map]
        if missing and not args.quiet:
            for n in missing:
                warn(f"Skill not found: {n}")

    # Check for remote skills
    remote_count = sum(
        1 for entry in entries if (manifest := load_manifest(entry.name)) and is_remote_source(manifest.source_path)
    )

    if remote_count > 0 and not args.quiet and not json_enabled(args.json):
        print(f"Checking {remote_count} remote skill(s)...", file=sys.stderr)

    synced = 0
    missing_count = 0
    modified_count = 0
    pruned = []
    results = []

    for index, entry in enumerate(entries, start=1):
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
            if is_remote and not args.quiet and not json_enabled(args.json):
                platform = (
                    "GitHub"
                    if "github.com" in manifest.source_path
                    else "GitLab"
                    if "gitlab.com" in manifest.source_path
                    else "remote"
                )
                progress_counter(index, len(entries), f"Checking {entry.name} ({platform})...")

            status = check_manifest(manifest)

            if is_remote and not args.quiet and not json_enabled(args.json):
                status_line("success", entry.name, "checked")

            if status.status == "missing":
                missing_count += 1
                status_info = status.to_dict()

                if args.prune:
                    remove_skill(entry.name)
                    pruned.append(entry.name)
                    status_info["pruned"] = True
            elif status.status == "modified":
                modified_count += 1
                # Update manifest
                new_manifest = sync_manifest(manifest)
                save_manifest(new_manifest)
                synced += 1
                status_info = {"name": entry.name, "status": "synced", "message": "Manifest updated"}
            else:
                status_info = status.to_dict()

        results.append(status_info)

    if json_enabled(args.json):
        json_output(
            {
                "synced": synced,
                "missing": missing_count,
                "modified": modified_count,
                "pruned": len(pruned),
                "results": results,
            },
            command="registry",
            v2=json_mode_v2,
        )
    else:
        for result in results:
            if result["status"] == "synced":
                status_line("success", result["name"], "synced")
            elif result["status"] == "modified":
                status_line("warning", result["name"], "modified (use --update)")
            elif result["status"] == "missing":
                msg = f"{result['name']}: missing"
                if result.get("pruned"):
                    msg += " (removed)"
                status_line("error", result["name"], msg.replace(f"{result['name']}: ", ""))
            else:
                status_line("success", result["name"], "up to date")

        summary({"synced": synced, "modified": modified_count, "missing": missing_count})
        if pruned:
            summary({"pruned": len(pruned)})

    return 1 if missing_count > 0 else 0


def run_prune(args: argparse.Namespace) -> int:
    """Clean up corrupted/missing skills and orphaned artifacts (oasr registry prune)."""
    from manifest import delete_manifest, list_manifests

    entries = load_registry()
    json_mode_v2 = json_v2(args.json)
    registered_names = {e.name for e in entries}
    manifest_names = set(list_manifests())

    to_remove_skills = []
    to_remove_manifests = []

    # Check for remote skills and show progress header
    remote_count = 0
    for entry in entries:
        manifest = load_manifest(entry.name)
        if manifest and is_remote_source(manifest.source_path):
            remote_count += 1

    if remote_count > 0 and not json_enabled(args.json):
        print(f"Checking {remote_count} remote skill(s)...", file=sys.stderr)

    for index, entry in enumerate(entries, start=1):
        manifest = load_manifest(entry.name)
        if manifest:
            # Show progress for remote skills
            is_remote = is_remote_source(manifest.source_path)
            if is_remote and not json_enabled(args.json):
                platform = (
                    "GitHub"
                    if "github.com" in manifest.source_path
                    else "GitLab"
                    if "gitlab.com" in manifest.source_path
                    else "remote"
                )
                progress_counter(index, len(entries), f"Checking {entry.name} ({platform})...")

            status = check_manifest(manifest)

            if is_remote and not json_enabled(args.json):
                status_line("success", entry.name, "checked")

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
        if json_enabled(args.json):
            json_output({"cleaned": 0, "message": "nothing to clean"}, command="registry", v2=json_mode_v2)
        else:
            print("Nothing to clean.")
        return 0

    if json_enabled(args.json):
        result = {
            "skills_to_remove": to_remove_skills,
            "manifests_to_remove": to_remove_manifests,
            "dry_run": args.dry_run,
        }
        if not args.dry_run and not args.yes:
            result["requires_confirmation"] = True
        json_output(result, command="registry", v2=json_mode_v2)
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

    if not args.yes and not json_enabled(args.json):
        if not require_confirmation("Proceed with cleanup?", yes_flag=args.yes, default=False):
            print("Aborted.")
            return 1

    removed_skills = []
    removed_manifests = []

    for s in to_remove_skills:
        remove_skill(s["name"])
        removed_skills.append(s["name"])

    for m in to_remove_manifests:
        delete_manifest(m["name"])
        removed_manifests.append(m["name"])

    if json_enabled(args.json):
        json_output(
            {"removed_skills": removed_skills, "removed_manifests": removed_manifests},
            command="registry",
            v2=json_mode_v2,
        )
    else:
        for name in removed_skills:
            print(f"Removed skill: {name}")
        for name in removed_manifests:
            print(f"Removed manifest: {name}")
        summary({"cleaned skills": len(removed_skills), "manifests": len(removed_manifests)})

    return 0
