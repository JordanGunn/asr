"""`oasr diff` command - show tracked skill status."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tracking import extract_metadata
from manifest import load_manifest, hash_directory


def register(subparsers) -> None:
    """Register the diff command."""
    p = subparsers.add_parser(
        "diff",
        help="Show status of tracked skills (copied with metadata)"
    )
    p.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Path to scan for tracked skills (default: current directory)"
    )
    p.add_argument("--json", action="store_true", help="Output in JSON format")
    p.add_argument("--quiet", action="store_true", help="Suppress info/warnings")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    """Show status of tracked skills in the given path."""
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
            print(json.dumps({"tracked": 0, "skills": []}))
        else:
            print("No tracked skills found.")
        return 0
    
    # Determine status for each tracked skill
    results = []
    up_to_date = 0
    outdated = 0
    modified = 0
    untracked = 0
    
    for skill_dir, metadata in tracked_skills:
        skill_name = skill_dir.name
        tracked_hash = metadata.get("hash")
        tracked_source = metadata.get("source")
        
        # Compute current file hash (excluding metadata.oasr for comparison)
        from tracking import strip_tracking_metadata
        from discovery import parse_frontmatter
        
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            frontmatter_dict = parse_frontmatter(content)
            if frontmatter_dict:
                # Strip tracking metadata for hash comparison
                cleaned_fm = strip_tracking_metadata(frontmatter_dict)
                # We'll compare hashes by temporarily computing without metadata
                # For now, just use the manifest hash comparison
        
        # For simplicity: check if tracked_hash matches registry hash
        # The tracked_hash should be the registry hash at time of copy
        from registry import load_registry
        entries = load_registry()
        entry = next((e for e in entries if e.name == skill_name), None)
        
        if entry:
            manifest = load_manifest(skill_name)
            if manifest:
                # Compare tracked hash with registry hash
                if manifest.content_hash == tracked_hash:
                    # Up to date
                    status = "up-to-date"
                    up_to_date += 1
                    message = "Current"
                else:
                    # Registry has changed
                    status = "outdated"
                    outdated += 1
                    message = "Registry has newer version"
            else:
                status = "untracked"
                untracked += 1
                message = "No manifest"
        else:
            status = "untracked"
            untracked += 1
            message = "Not in registry"
        
        results.append({
            "name": skill_name,
            "path": str(skill_dir),
            "status": status,
            "message": message,
            "tracked_hash": tracked_hash[:16] + "..." if tracked_hash else None,
            "source": tracked_source,
        })
    
    if args.json:
        print(
            json.dumps(
                {
                    "tracked": len(tracked_skills),
                    "up_to_date": up_to_date,
                    "outdated": outdated,
                    "modified": modified,
                    "untracked": untracked,
                    "skills": results,
                },
                indent=2,
            )
        )
    else:
        # Git-style output
        for result in results:
            if result["status"] == "up-to-date":
                symbol = "✓"
            elif result["status"] == "outdated":
                symbol = "⚠"
            elif result["status"] == "modified":
                symbol = "✗"
            else:
                symbol = "?"
            
            print(f"{symbol} {result['name']}: {result['status']}")
            if not args.quiet:
                print(f"  Path: {result['path']}")
                if result["message"]:
                    print(f"  {result['message']}")
        
        print(f"\n{len(tracked_skills)} tracked: {up_to_date} up-to-date, {outdated} outdated, {modified} modified, {untracked} untracked")
        
        if outdated > 0:
            print(f"\nRun 'oasr sync' to update outdated skills.")
    
    return 1 if outdated > 0 or modified > 0 else 0
