"""Pure Python adapter generation - self-contained and portable.

This module provides standalone adapter generation for Cursor, Windsurf, and Codex
without dependencies on other CLI modules. Can be used as a library or run directly.

Usage:
    python -m skills.adapter --skills-root /path/to/skills --output-dir /path/to/project
    python -m skills.adapter --skills-root /path/to/skills --target cursor
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class SkillInfo:
    """Discovered skill information."""

    name: str
    description: str
    path: Path


def parse_frontmatter(content: str) -> dict[str, str]:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown file content.

    Returns:
        Dictionary of frontmatter fields, empty if no valid frontmatter.
    """
    if not content.startswith("---"):
        return {}

    lines = content.split("\n")
    end_idx = -1

    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return {}

    fm_text = "\n".join(lines[1:end_idx])

    if HAS_YAML:
        try:
            parsed = yaml.safe_load(fm_text)
            if isinstance(parsed, dict):
                return {k: str(v) if v else "" for k, v in parsed.items()}
        except yaml.YAMLError:
            pass

    frontmatter = {}
    for line in lines[1:end_idx]:
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    return frontmatter


def find_skills(root: Path) -> list[SkillInfo]:
    """Recursively find all SKILL.md files and extract skill info.

    Args:
        root: Root directory to search.

    Returns:
        List of discovered skills with name, description, and path.
    """
    skills = []

    for skill_md in root.rglob("SKILL.md"):
        skill_dir = skill_md.parent

        try:
            content = skill_md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        fm = parse_frontmatter(content)
        name = fm.get("name", skill_dir.name)
        description = fm.get("description", "")

        if not name:
            continue

        skills.append(
            SkillInfo(
                name=name,
                description=description,
                path=skill_dir.resolve(),
            )
        )

    return skills


def generate_cursor(skill: SkillInfo, output_dir: Path) -> Path:
    """Generate a Cursor command file.

    Args:
        skill: Skill information.
        output_dir: Target directory (will create .cursor/commands/).

    Returns:
        Path to the generated file.
    """
    target_dir = output_dir / ".cursor" / "commands"
    target_dir.mkdir(parents=True, exist_ok=True)

    output_file = target_dir / f"{skill.name}.md"

    content = f"""# {skill.name}

{skill.description}

This command delegates to the agent skill at `{skill.path}/`.

## Skill Location

- **Path:** `{skill.path}/`
- **Manifest:** `{skill.path}/SKILL.md`
"""

    output_file.write_text(content, encoding="utf-8")
    return output_file


def generate_windsurf(skill: SkillInfo, output_dir: Path) -> Path:
    """Generate a Windsurf workflow file.

    Args:
        skill: Skill information.
        output_dir: Target directory (will create .windsurf/workflows/).

    Returns:
        Path to the generated file.
    """
    target_dir = output_dir / ".windsurf" / "workflows"
    target_dir.mkdir(parents=True, exist_ok=True)

    output_file = target_dir / f"{skill.name}.md"

    desc_yaml = json.dumps(skill.description)

    content = f"""---
description: {desc_yaml}
auto_execution_mode: 1
---

# {skill.name}

This workflow delegates to the agent skill at `{skill.path}/`.

## Skill Location

- **Path:** `{skill.path}/`
- **Manifest:** `{skill.path}/SKILL.md`
"""

    output_file.write_text(content, encoding="utf-8")
    return output_file


def generate_codex(skill: SkillInfo, output_dir: Path) -> Path:
    """Generate a Codex skill file (placeholder, uses Cursor format).

    Args:
        skill: Skill information.
        output_dir: Target directory (will create .codex/skills/).

    Returns:
        Path to the generated file.
    """
    target_dir = output_dir / ".codex" / "skills"
    target_dir.mkdir(parents=True, exist_ok=True)

    output_file = target_dir / f"{skill.name}.md"

    content = f"""# {skill.name}

{skill.description}

This skill delegates to the agent skill at `{skill.path}/`.

## Skill Location

- **Path:** `{skill.path}/`
- **Manifest:** `{skill.path}/SKILL.md`
"""

    output_file.write_text(content, encoding="utf-8")
    return output_file


def cleanup_stale(
    output_dir: Path,
    subdir: str,
    valid_names: set[str],
    marker: str,
) -> list[Path]:
    """Remove stale generated files.

    Args:
        output_dir: Base output directory.
        subdir: Subdirectory path (e.g., ".cursor/commands").
        valid_names: Set of valid skill names to keep.
        marker: Text marker to identify generated files.

    Returns:
        List of removed file paths.
    """
    removed = []
    target_dir = output_dir / subdir

    if not target_dir.is_dir():
        return removed

    for file in target_dir.glob("*.md"):
        name = file.stem

        if name in valid_names:
            continue

        try:
            content = file.read_text(encoding="utf-8")
            if marker in content:
                file.unlink()
                removed.append(file)
        except (OSError, UnicodeDecodeError):
            pass

    return removed


ADAPTERS: dict[str, tuple[Callable[[SkillInfo, Path], Path], str, str]] = {
    "cursor": (generate_cursor, ".cursor/commands", "This command delegates to the agent skill at"),
    "windsurf": (generate_windsurf, ".windsurf/workflows", "This workflow delegates to the agent skill at"),
    "codex": (generate_codex, ".codex/skills", "This skill delegates to the agent skill at"),
}


def generate_adapters(
    skills_root: Path,
    output_dir: Path,
    targets: list[str] | None = None,
    exclude: set[str] | None = None,
    cleanup: bool = True,
) -> dict[str, dict]:
    """Generate adapter files for all skills.

    Args:
        skills_root: Root directory containing skills.
        output_dir: Output directory for generated files.
        targets: List of adapter targets (default: all).
        exclude: Set of skill names to exclude.
        cleanup: Whether to remove stale files.

    Returns:
        Dictionary with results per target.
    """
    if targets is None:
        targets = list(ADAPTERS.keys())

    if exclude is None:
        exclude = set()

    skills = find_skills(skills_root)
    skills = [s for s in skills if s.name not in exclude]
    valid_names = {s.name for s in skills}

    results = {}

    for target in targets:
        if target not in ADAPTERS:
            continue

        generator, subdir, marker = ADAPTERS[target]
        generated = []
        removed = []

        for skill in skills:
            path = generator(skill, output_dir)
            generated.append(path)

        if cleanup:
            removed = cleanup_stale(output_dir, subdir, valid_names, marker)

        results[target] = {
            "generated": [str(p) for p in generated],
            "removed": [str(p) for p in removed],
            "output_dir": str(output_dir / subdir),
        }

    return results


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for standalone adapter generation."""
    parser = argparse.ArgumentParser(
        prog="skills.adapter",
        description="Generate IDE adapter files from SKILL.md files.",
    )
    parser.add_argument(
        "--skills-root",
        type=Path,
        required=True,
        help="Root directory containing skills",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Output directory (default: current)",
    )
    parser.add_argument(
        "--target",
        choices=list(ADAPTERS.keys()),
        action="append",
        dest="targets",
        help="Target adapter(s) to generate (default: all)",
    )
    parser.add_argument(
        "--exclude",
        help="Comma-separated skill names to exclude",
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Don't remove stale files",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output",
    )

    args = parser.parse_args(argv)

    skills_root = args.skills_root.resolve()
    output_dir = args.output_dir.resolve()

    if not skills_root.is_dir():
        print(f"Error: Not a directory: {skills_root}", file=sys.stderr)
        return 2

    exclude = set()
    if args.exclude:
        exclude = set(args.exclude.split(","))

    results = generate_adapters(
        skills_root=skills_root,
        output_dir=output_dir,
        targets=args.targets,
        exclude=exclude,
        cleanup=not args.no_cleanup,
    )

    if args.json:
        print(json.dumps(results, indent=2))
    elif not args.quiet:
        for target, info in results.items():
            gen_count = len(info["generated"])
            rem_count = len(info["removed"])
            print(f"{target}: Generated {gen_count} file(s) in {info['output_dir']}")
            if rem_count:
                print(f"  Removed {rem_count} stale file(s)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
