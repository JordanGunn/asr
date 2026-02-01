"""`oasr clone` command - copy skill(s) to target directory."""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path

from registry import load_registry
from skillcopy import copy_skill


def register(subparsers) -> None:
    """Register the clone command."""
    p = subparsers.add_parser(
        "clone",
        help="Clone skill(s) to target directory",
        description="Clone skills from the registry to a target directory with tracking metadata",
    )
    p.add_argument("names", nargs="+", help="Skill name(s) or glob pattern(s) to clone")
    p.add_argument(
        "-d",
        "--dir",
        type=Path,
        default=Path("."),
        dest="output_dir",
        help="Target directory (default: current)",
    )
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.set_defaults(func=run)


def _match_skills(patterns: list[str], entry_map: dict) -> tuple[list[str], list[str]]:
    """Match skill names against patterns (exact or glob).

    Returns:
        Tuple of (matched_names, unmatched_patterns).
    """
    matched = set()
    unmatched = []
    all_names = list(entry_map.keys())

    for pattern in patterns:
        if pattern in entry_map:
            matched.add(pattern)
        elif any(c in pattern for c in "*?["):
            # Glob pattern
            matches = fnmatch.filter(all_names, pattern)
            if matches:
                matched.update(matches)
            else:
                unmatched.append(pattern)
        else:
            unmatched.append(pattern)

    return list(matched), unmatched


def run(args: argparse.Namespace) -> int:
    """Execute the clone command."""
    entries = load_registry()
    entry_map = {e.name: e for e in entries}

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    warnings = []

    matched_names, unmatched = _match_skills(args.names, entry_map)

    for pattern in unmatched:
        warnings.append(f"No skills matched: {pattern}")

    # Get manifests for tracking metadata
    from manifest import load_manifest

    # Separate remote and local skills for parallel processing
    from skillcopy.remote import is_remote_source

    remote_names = [name for name in matched_names if is_remote_source(entry_map[name].path)]
    local_names = [name for name in matched_names if not is_remote_source(entry_map[name].path)]

    # Handle remote skills with parallel fetching
    if remote_names:
        print(f"Fetching {len(remote_names)} remote skill(s)...", file=sys.stderr)
        import threading
        from concurrent.futures import ThreadPoolExecutor, as_completed

        print_lock = threading.Lock()

        def copy_remote_entry(name):
            """Copy a remote skill with thread-safe progress."""
            entry = entry_map[name]
            dest = output_dir / name

            try:
                with print_lock:
                    platform = (
                        "GitHub" if "github.com" in entry.path else "GitLab" if "gitlab.com" in entry.path else "remote"
                    )
                    print(f"  ↓ {name} (fetching from {platform}...)", file=sys.stderr, flush=True)

                # Get manifest hash for tracking
                manifest = load_manifest(name)
                source_hash = manifest.content_hash if manifest else None

                copy_skill(
                    entry.path,
                    dest,
                    validate=False,
                    show_progress=False,
                    skill_name=name,
                    inject_tracking=True,
                    source_hash=source_hash,
                )

                with print_lock:
                    print(f"  ✓ {name} (downloaded)", file=sys.stderr)

                return {"name": name, "src": entry.path, "dest": str(dest)}, None
            except Exception as e:
                with print_lock:
                    print(f"  ✗ {name} ({str(e)[:50]}...)", file=sys.stderr)
                return None, f"Failed to clone {name}: {e}"

        # Copy remote skills in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(copy_remote_entry, name): name for name in remote_names}

            for future in as_completed(futures):
                result, error = future.result()
                if result:
                    copied.append(result)
                if error:
                    warnings.append(error)

    # Handle local skills sequentially (fast anyway)
    for name in sorted(local_names):
        entry = entry_map[name]
        dest = output_dir / name

        try:
            # Get manifest hash for tracking
            manifest = load_manifest(name)
            source_hash = manifest.content_hash if manifest else None

            # Unified copy with tracking
            copy_skill(entry.path, dest, validate=False, inject_tracking=True, source_hash=source_hash)
            copied.append({"name": name, "src": entry.path, "dest": str(dest)})
        except Exception as e:
            warnings.append(f"Failed to clone {name}: {e}")

    if not args.quiet:
        for w in warnings:
            print(f"⚠ {w}", file=sys.stderr)

    if args.json:
        print(
            json.dumps(
                {
                    "copied": len(copied),
                    "warnings": len(warnings),
                    "skills": copied,
                },
                indent=2,
            )
        )
    else:
        for c in copied:
            print(f"Cloned: {c['name']} → {c['dest']}")
        if copied:
            print(f"\n{len(copied)} skill(s) cloned to {output_dir}")

    return 1 if warnings and not copied else 0
