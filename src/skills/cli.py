"""CLI entry point and command definitions."""

import argparse
import json
import shutil
import sys
from pathlib import Path

from skills import __version__
from skills.config import load_config
from skills.registry import (
    SkillEntry,
    load_registry,
    add_skill,
    remove_skill,
)
from skills.discovery import find_skills, discover_single
from skills.validation import validate_skill, validate_all
from skills.adapters import CursorAdapter, WindsurfAdapter, CodexAdapter
from skills.manifest import (
    load_manifest,
    check_manifest,
    sync_manifest,
    save_manifest,
    create_manifest,
    delete_manifest,
    list_manifests,
)


ADAPTERS = {
    "cursor": CursorAdapter(),
    "windsurf": WindsurfAdapter(),
    "codex": CodexAdapter(),
}


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except Exception as e:
        if args.json if hasattr(args, "json") else False:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 3


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="asr",
        description="Manage agent skills across IDE integrations.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Override config file path",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress info and warnings",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    _add_list_parser(subparsers)
    _add_add_parser(subparsers)
    _add_rm_parser(subparsers)
    _add_use_parser(subparsers)
    _add_find_parser(subparsers)
    _add_validate_parser(subparsers)
    _add_sync_parser(subparsers)
    _add_status_parser(subparsers)
    _add_clean_parser(subparsers)
    _add_adapter_parser(subparsers)
    
    return parser


def _add_list_parser(subparsers) -> None:
    """Add 'list' subcommand."""
    p = subparsers.add_parser("list", help="List registered skills")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.set_defaults(func=cmd_list)


def _add_add_parser(subparsers) -> None:
    """Add 'add' subcommand."""
    p = subparsers.add_parser("add", help="Register a skill")
    p.add_argument("path", type=Path, help="Path to skill directory (or root for recursive)")
    p.add_argument("-r", "--recursive", action="store_true", help="Recursively add all valid skills from path")
    p.add_argument("--strict", action="store_true", help="Fail if validation has warnings")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.add_argument("--config", type=Path, help="Override config file path")
    p.set_defaults(func=cmd_add)


def _add_rm_parser(subparsers) -> None:
    """Add 'rm' subcommand."""
    p = subparsers.add_parser("rm", help="Unregister a skill")
    p.add_argument("name_or_path", help="Skill name or path to remove")
    p.add_argument("-r", "--recursive", action="store_true", help="Recursively remove all skills under path")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.set_defaults(func=cmd_rm)


def _add_use_parser(subparsers) -> None:
    """Add 'use' subcommand."""
    p = subparsers.add_parser("use", help="Copy skill(s) to target directory")
    p.add_argument("names", nargs="+", help="Skill name(s) to copy")
    p.add_argument("-d", "--dir", type=Path, default=Path("."), dest="output_dir", help="Target directory (default: current)")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.set_defaults(func=cmd_use)


def _add_find_parser(subparsers) -> None:
    """Add 'find' subcommand."""
    p = subparsers.add_parser("find", help="Find skills recursively")
    p.add_argument("root", type=Path, help="Root directory to search")
    p.add_argument("--add", action="store_true", dest="add_found", help="Register found skills")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.set_defaults(func=cmd_find)


def _add_validate_parser(subparsers) -> None:
    """Add 'validate' subcommand."""
    p = subparsers.add_parser("validate", help="Validate skills")
    p.add_argument("path", type=Path, nargs="?", help="Path to skill directory")
    p.add_argument("--all", action="store_true", dest="validate_all", help="Validate all registered skills")
    p.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.add_argument("--config", type=Path, help="Override config file path")
    p.set_defaults(func=cmd_validate)


def _add_sync_parser(subparsers) -> None:
    """Add 'sync' subcommand."""
    p = subparsers.add_parser("sync", help="Sync skills from source (using manifests)")
    p.add_argument("names", nargs="*", help="Skill name(s) to sync (default: all)")
    p.add_argument("-d", "--dir", type=Path, dest="output_dir", help="Target directory to copy skills to")
    p.add_argument("--update", action="store_true", help="Update manifests for modified skills")
    p.add_argument("--prune", action="store_true", help="Remove skills with missing sources from registry")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.add_argument("--config", type=Path, help="Override config file path")
    p.set_defaults(func=cmd_sync)


def _add_status_parser(subparsers) -> None:
    """Add 'status' subcommand."""
    p = subparsers.add_parser("status", help="Show skill manifest status")
    p.add_argument("names", nargs="*", help="Skill name(s) to check (default: all)")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.set_defaults(func=cmd_status)


def _add_clean_parser(subparsers) -> None:
    """Add 'clean' subcommand."""
    p = subparsers.add_parser("clean", help="Clean up corrupted/missing skills and orphaned artifacts")
    p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--dry-run", action="store_true", help="Show what would be cleaned without doing it")
    p.set_defaults(func=cmd_clean)


def _add_adapter_parser(subparsers) -> None:
    """Add 'adapter' subcommand with nested subcommands."""
    p = subparsers.add_parser("adapter", help="Generate IDE-specific files")
    p.add_argument("--exclude", help="Comma-separated skill names to exclude")
    p.add_argument("--output-dir", type=Path, default=Path("."), help="Output directory")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.add_argument("--config", type=Path, help="Override config file path")
    
    adapter_subs = p.add_subparsers(dest="target", help="Target IDE")
    
    for name in ["cursor", "windsurf", "codex"]:
        sp = adapter_subs.add_parser(name, help=f"Generate {name} files")
        sp.add_argument("--exclude", help="Comma-separated skill names to exclude")
        sp.add_argument("--output-dir", type=Path, default=Path("."), help="Output directory")
        sp.add_argument("--json", action="store_true", help="Output in JSON format")
        sp.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
        sp.add_argument("--config", type=Path, help="Override config file path")
    
    p.set_defaults(func=cmd_adapter)


def cmd_list(args: argparse.Namespace) -> int:
    """List registered skills."""
    entries = load_registry()
    
    if not entries:
        if args.json:
            print("[]")
        else:
            print("No skills registered. Use 'asr add <path>' to register a skill.")
        return 0
    
    if args.json:
        data = [{"name": e.name, "description": e.description, "path": e.path} for e in entries]
        print(json.dumps(data, indent=2))
    else:
        name_width = max(len(e.name) for e in entries)
        for e in entries:
            desc = e.description[:50] + "..." if len(e.description) > 50 else e.description
            print(f"{e.name:<{name_width}}  {desc:<55}  {e.path}")
    
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    """Register a skill."""
    path = args.path.resolve()
    config = load_config(args.config)
    max_lines = config["validation"]["reference_max_lines"]
    
    if args.recursive:
        return _cmd_add_recursive(args, path, max_lines)
    
    result = validate_skill(path, reference_max_lines=max_lines)
    
    if not args.quiet:
        _print_validation_result(result, args.json)
    
    if not result.valid:
        if args.json:
            print(json.dumps({"added": False, "reason": "validation errors"}))
        else:
            print("Cannot add skill: validation errors")
        return 1
    
    if args.strict and result.warnings:
        if args.json:
            print(json.dumps({"added": False, "reason": "validation warnings (strict mode)"}))
        else:
            print("Cannot add skill: validation warnings in strict mode")
        return 1
    
    discovered = discover_single(path)
    if not discovered:
        print("Error: Could not discover skill info", file=sys.stderr)
        return 3
    
    entry = SkillEntry(
        path=str(discovered.path),
        name=discovered.name,
        description=discovered.description,
    )
    
    is_new = add_skill(entry)
    
    if args.json:
        print(json.dumps({"added": True, "new": is_new, "name": entry.name}))
    else:
        action = "Added" if is_new else "Updated"
        print(f"{action} skill: {entry.name}")
    
    return 0


def _cmd_add_recursive(args: argparse.Namespace, root: Path, max_lines: int) -> int:
    """Recursively add all valid skills from root."""
    if not root.is_dir():
        print(f"Error: Not a directory: {root}", file=sys.stderr)
        return 2
    
    skills = find_skills(root)
    if not skills:
        if args.json:
            print(json.dumps({"added": 0, "skipped": 0, "skills": []}))
        else:
            print(f"No skills found under {root}")
        return 0
    
    added_count = 0
    skipped_count = 0
    results = []
    
    for s in skills:
        result = validate_skill(s.path, reference_max_lines=max_lines)
        
        if not result.valid:
            skipped_count += 1
            if not args.quiet:
                print(f"⚠ Skipping {s.name}: validation errors", file=sys.stderr)
            results.append({"name": s.name, "added": False, "reason": "validation errors"})
            continue
        
        if args.strict and result.warnings:
            skipped_count += 1
            if not args.quiet:
                print(f"⚠ Skipping {s.name}: validation warnings (strict)", file=sys.stderr)
            results.append({"name": s.name, "added": False, "reason": "validation warnings"})
            continue
        
        entry = SkillEntry(path=str(s.path), name=s.name, description=s.description)
        is_new = add_skill(entry)
        added_count += 1
        
        if not args.quiet and not args.json:
            action = "Added" if is_new else "Updated"
            print(f"{action}: {s.name}")
        
        results.append({"name": s.name, "added": True, "new": is_new})
    
    if args.json:
        print(json.dumps({"added": added_count, "skipped": skipped_count, "skills": results}, indent=2))
    elif not args.quiet:
        print(f"\n{added_count} skill(s) added, {skipped_count} skipped")
    
    return 0


def cmd_rm(args: argparse.Namespace) -> int:
    """Unregister a skill."""
    if args.recursive:
        return _cmd_rm_recursive(args)
    
    removed = remove_skill(args.name_or_path)
    
    if args.json:
        print(json.dumps({"removed": removed}))
    else:
        if removed:
            print(f"Removed: {args.name_or_path}")
        else:
            print(f"Not found: {args.name_or_path}")
    
    return 0 if removed else 1


def _cmd_rm_recursive(args: argparse.Namespace) -> int:
    """Recursively remove all skills under a path."""
    root = Path(args.name_or_path).resolve()
    
    if not root.is_dir():
        print(f"Error: Not a directory: {root}", file=sys.stderr)
        return 2
    
    entries = load_registry()
    root_str = str(root)
    
    to_remove = [e for e in entries if e.path.startswith(root_str)]
    
    if not to_remove:
        if args.json:
            print(json.dumps({"removed": 0, "skills": []}))
        else:
            print(f"No registered skills found under {root}")
        return 0
    
    removed_names = []
    for entry in to_remove:
        remove_skill(entry.name)
        removed_names.append(entry.name)
    
    if args.json:
        print(json.dumps({"removed": len(removed_names), "skills": removed_names}))
    else:
        for name in removed_names:
            print(f"Removed: {name}")
        print(f"\n{len(removed_names)} skill(s) removed")
    
    return 0


def cmd_use(args: argparse.Namespace) -> int:
    """Copy skill(s) to target directory."""
    entries = load_registry()
    entry_map = {e.name: e for e in entries}
    
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    copied = []
    warnings = []
    
    for name in args.names:
        if name not in entry_map:
            warnings.append(f"Skill not found: {name} (run 'asr validate' or 'asr add')")
            continue
        
        entry = entry_map[name]
        src = Path(entry.path)
        
        if not src.exists():
            warnings.append(f"Skill path missing: {name} at {entry.path}")
            continue
        
        dest = output_dir / name
        
        if dest.exists():
            shutil.rmtree(dest)
        
        shutil.copytree(src, dest)
        copied.append({"name": name, "src": str(src), "dest": str(dest)})
    
    if not args.quiet:
        for w in warnings:
            print(f"⚠ {w}", file=sys.stderr)
    
    if args.json:
        print(json.dumps({
            "copied": len(copied),
            "warnings": len(warnings),
            "skills": copied,
        }, indent=2))
    else:
        for c in copied:
            print(f"Copied: {c['name']} → {c['dest']}")
        if copied:
            print(f"\n{len(copied)} skill(s) copied to {output_dir}")
    
    return 1 if warnings and not copied else 0


def cmd_find(args: argparse.Namespace) -> int:
    """Find skills recursively."""
    root = args.root.resolve()
    
    if not root.is_dir():
        print(f"Error: Not a directory: {root}", file=sys.stderr)
        return 2
    
    skills = find_skills(root)
    
    if args.json:
        data = [{"name": s.name, "description": s.description, "path": str(s.path)} for s in skills]
        print(json.dumps(data, indent=2))
    else:
        if not skills:
            print(f"No skills found under {root}")
        else:
            for s in skills:
                print(f"{s.name:<30}  {s.path}")
    
    if args.add_found and skills:
        added = 0
        for s in skills:
            entry = SkillEntry(
                path=str(s.path),
                name=s.name,
                description=s.description,
            )
            if add_skill(entry):
                added += 1
        
        if not args.json and not args.quiet:
            print(f"\nRegistered {added} new skill(s), {len(skills) - added} updated.")
    
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate skills."""
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
            _print_validation_result(result, json_output=False)
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


def cmd_adapter(args: argparse.Namespace) -> int:
    """Generate IDE-specific files."""
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
        generated, removed = adapter.generate_all(entries, output_dir, exclude)
        
        total_generated += len(generated)
        total_removed += len(removed)
        
        results[target] = {
            "generated": len(generated),
            "removed": len(removed),
            "output_dir": str(adapter.resolve_output_dir(output_dir)),
        }
    
    if args.json:
        print(json.dumps({
            "total_generated": total_generated,
            "total_removed": total_removed,
            "targets": results,
        }, indent=2))
    else:
        for target, info in results.items():
            print(f"{target}: Generated {info['generated']} file(s) in {info['output_dir']}")
            if info['removed']:
                print(f"  Removed {info['removed']} stale file(s)")
    
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    """Sync skills from source using manifests."""
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
            status = check_manifest(manifest)
            
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
        print(json.dumps({
            "synced": synced,
            "missing": missing_count,
            "modified": modified_count,
            "pruned": pruned,
            "skills": results,
        }, indent=2))
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


def cmd_status(args: argparse.Namespace) -> int:
    """Show skill manifest status."""
    entries = load_registry()
    
    if not entries:
        if args.json:
            print("[]")
        else:
            print("No skills registered.")
        return 0
    
    if args.names:
        entry_map = {e.name: e for e in entries}
        entries = [entry_map[n] for n in args.names if n in entry_map]
    
    results = []
    
    for entry in entries:
        manifest = load_manifest(entry.name)
        
        if manifest is None:
            status_info = {
                "name": entry.name,
                "status": "untracked",
                "source_path": entry.path,
                "message": "No manifest (run 'asr sync' to create)",
            }
        else:
            status = check_manifest(manifest)
            status_info = status.to_dict()
        
        results.append(status_info)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            status = r.get("status", "unknown")
            name = r.get("name", "?")
            
            if status == "valid":
                print(f"✓ {name}")
            elif status == "untracked":
                print(f"? {name} (untracked)")
            elif status == "missing":
                print(f"✗ {name} (source missing)")
            elif status == "modified":
                print(f"⚠ {name} (modified)")
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
    
    if not args.json:
        print(f"\n{valid} valid, {modified} modified, {missing} missing, {untracked} untracked")
    
    return 0


def cmd_clean(args: argparse.Namespace) -> int:
    """Clean up corrupted/missing skills and orphaned artifacts."""
    entries = load_registry()
    registered_names = {e.name for e in entries}
    manifest_names = set(list_manifests())
    
    to_remove_skills = []
    to_remove_manifests = []
    
    for entry in entries:
        manifest = load_manifest(entry.name)
        if manifest:
            status = check_manifest(manifest)
            if status.status == "missing":
                to_remove_skills.append({
                    "name": entry.name,
                    "reason": "source missing",
                    "path": entry.path,
                })
    
    orphaned = manifest_names - registered_names
    for name in orphaned:
        to_remove_manifests.append({
            "name": name,
            "reason": "orphaned manifest (not in registry)",
        })
    
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
        print(json.dumps({
            "removed_skills": removed_skills,
            "removed_manifests": removed_manifests,
        }, indent=2))
    else:
        for name in removed_skills:
            print(f"Removed skill: {name}")
        for name in removed_manifests:
            print(f"Removed manifest: {name}")
        print(f"\nCleaned {len(removed_skills)} skill(s), {len(removed_manifests)} manifest(s)")
    
    return 0


def _print_validation_result(result, json_output: bool) -> None:
    """Print a validation result."""
    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return
    
    print(f"{result.name}")
    
    if result.valid and not result.warnings:
        print("  ✓ Valid")
    else:
        for msg in result.all_messages:
            print(f"  {msg}")


if __name__ == "__main__":
    sys.exit(main())
