"""`asr add` command."""

from __future__ import annotations

import argparse
import glob as globlib
import json
import shutil
import sys
from pathlib import Path

from config import load_config
from discovery import discover_single, find_skills
from registry import SkillEntry, add_skill
from remote import InvalidRemoteUrlError, derive_skill_name, fetch_remote_to_temp, validate_remote_url
from skillcopy.remote import is_remote_source
from validate import validate_skill

_GLOB_CHARS = set("*?[")


def _looks_like_glob(value: str) -> bool:
    return any(ch in value for ch in _GLOB_CHARS)


def _expand_path_patterns(patterns: list[str]) -> list[Path]:
    expanded: list[Path] = []
    for raw in patterns:
        pat = str(Path(raw).expanduser())
        if _looks_like_glob(pat):
            matches = globlib.glob(pat, recursive=True)
            expanded.extend(Path(m) for m in matches)
        else:
            expanded.append(Path(pat))
    return expanded


def _print_validation_result(result) -> None:
    print(f"{result.name}")
    if result.valid and not result.warnings:
        print("  ✓ Valid")
    else:
        for msg in result.all_messages:
            print(f"  {msg}")


def register(subparsers) -> None:
    p = subparsers.add_parser("add", help="Register a skill")
    p.add_argument(
        "paths",
        nargs="+",
        help="Path(s), URL(s), or glob pattern(s) to skill dir(s) (or root(s) for recursive)",
    )
    p.add_argument("-r", "--recursive", action="store_true", help="Recursively add all valid skills from path")
    p.add_argument("--strict", action="store_true", help="Fail if validation has warnings")
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.add_argument("--config", type=Path, help="Override config file path")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    max_lines = config["validation"]["reference_max_lines"]

    # Separate remote URLs from local paths
    remote_urls = []
    local_patterns = []

    for pattern in args.paths:
        if is_remote_source(pattern):
            remote_urls.append(pattern)
        else:
            local_patterns.append(pattern)

    # Expand local paths
    expanded = []
    if local_patterns:
        expanded = [p.resolve() for p in _expand_path_patterns(local_patterns)]

    # Check if we have anything to process
    if not expanded and not remote_urls:
        if args.json:
            print(json.dumps({"added": 0, "skipped": 0, "skills": [], "error": "no paths matched"}))
        else:
            print("No paths matched.", file=sys.stderr)
        return 2

    # Handle recursive mode (local paths only)
    if args.recursive:
        if remote_urls:
            print("Warning: --recursive flag ignored for remote URLs", file=sys.stderr)
        exit_code = 0
        for root in expanded:
            code = _run_recursive(args, root, max_lines)
            if code != 0:
                exit_code = code
        return exit_code

    results: list[dict] = []
    added_count = 0
    skipped_count = 0
    exit_code = 0

    # Process remote URLs
    for url in remote_urls:
        # Validate URL format
        valid, error_msg = validate_remote_url(url)
        if not valid:
            skipped_count += 1
            results.append({"url": url, "added": False, "reason": f"Invalid URL: {error_msg}"})
            exit_code = 1
            if not args.quiet and not args.json:
                print(f"Invalid URL: {url} - {error_msg}", file=sys.stderr)
            continue

        # Derive skill name
        try:
            derive_skill_name(url)
        except InvalidRemoteUrlError as e:
            skipped_count += 1
            results.append({"url": url, "added": False, "reason": str(e)})
            exit_code = 1
            if not args.quiet and not args.json:
                print(f"Cannot derive name from URL: {url}", file=sys.stderr)
            continue

        # Fetch to temp dir for validation
        try:
            if not args.quiet and not args.json:
                # Determine platform for user feedback
                if "github.com" in url:
                    platform = "GitHub"
                elif "gitlab.com" in url:
                    platform = "GitLab"
                else:
                    platform = "remote source"
                print(f"Registering from {platform}...", file=sys.stderr)

            temp_dir = fetch_remote_to_temp(url)

            if not args.quiet and not args.json:
                # Count files validated
                file_count = sum(1 for _ in temp_dir.rglob("*") if _.is_file())
                print(f"✓ Validated {file_count} file(s)", file=sys.stderr)
        except Exception as e:
            skipped_count += 1
            results.append({"url": url, "added": False, "reason": f"Fetch failed: {e}"})
            exit_code = 1
            if not args.quiet and not args.json:
                print(f"Failed to fetch {url}: {e}", file=sys.stderr)
            continue

        try:
            # Validate fetched content (skip name match for temp directory)
            result = validate_skill(temp_dir, reference_max_lines=max_lines, skip_name_match=True)
            if not args.quiet and not args.json:
                _print_validation_result(result)
                print()

            if not result.valid:
                skipped_count += 1
                results.append({"url": url, "added": False, "reason": "validation errors"})
                exit_code = 1
                continue

            if args.strict and result.warnings:
                skipped_count += 1
                results.append({"url": url, "added": False, "reason": "validation warnings (strict mode)"})
                exit_code = 1
                continue

            # Discover skill info from fetched content
            discovered = discover_single(temp_dir)
            if not discovered:
                skipped_count += 1
                results.append({"url": url, "added": False, "reason": "could not discover skill info"})
                exit_code = 3
                continue

            # Create entry with URL as source_path
            entry = SkillEntry(
                path=url,  # Store URL, not temp path
                name=discovered.name,
                description=discovered.description,
            )

            is_new = add_skill(entry)
            added_count += 1
            results.append({"name": entry.name, "url": url, "added": True, "new": is_new})

            if not args.quiet and not args.json:
                action = "Added" if is_new else "Updated"
                print(f"{action} remote skill: {entry.name} from {url}")

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    # Process local paths
    for path in expanded:
        if not path.exists():
            skipped_count += 1
            results.append({"path": str(path), "added": False, "reason": "path missing"})
            exit_code = 1
            if not args.quiet and not args.json:
                print(f"Not found: {path}", file=sys.stderr)
            continue

        result = validate_skill(path, reference_max_lines=max_lines)
        if not args.quiet and not args.json:
            _print_validation_result(result)
            print()

        if not result.valid:
            skipped_count += 1
            results.append({"path": str(path), "added": False, "reason": "validation errors"})
            exit_code = 1
            continue

        if args.strict and result.warnings:
            skipped_count += 1
            results.append({"path": str(path), "added": False, "reason": "validation warnings (strict mode)"})
            exit_code = 1
            continue

        discovered = discover_single(path)
        if not discovered:
            skipped_count += 1
            results.append({"path": str(path), "added": False, "reason": "could not discover skill info"})
            exit_code = 3
            continue

        entry = SkillEntry(
            path=str(discovered.path),
            name=discovered.name,
            description=discovered.description,
        )

        is_new = add_skill(entry)
        added_count += 1
        results.append({"name": entry.name, "path": entry.path, "added": True, "new": is_new})

        if not args.quiet and not args.json:
            action = "Added" if is_new else "Updated"
            print(f"{action} skill: {entry.name}")

    if args.json:
        print(json.dumps({"added": added_count, "skipped": skipped_count, "skills": results}, indent=2))

    return exit_code


def _run_recursive(args: argparse.Namespace, root: Path, max_lines: int) -> int:
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
