"""Discovery module for finding SKILL.md files recursively."""

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class DiscoveredSkill:
    """A discovered skill from filesystem."""

    path: Path
    name: str
    description: str
    raw_frontmatter: dict | None = None


def parse_frontmatter(content: str) -> dict | None:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown file content.

    Returns:
        Parsed frontmatter dictionary, or None if not found/invalid.
    """
    if not content.startswith("---"):
        return None

    lines = content.split("\n")
    end_idx = None

    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None

    frontmatter_text = "\n".join(lines[1:end_idx])

    try:
        return yaml.safe_load(frontmatter_text)
    except yaml.YAMLError:
        return None


def extract_skill_info(skill_md_path: Path) -> tuple[str, str, dict | None]:
    """Extract name and description from SKILL.md.

    Args:
        skill_md_path: Path to SKILL.md file.

    Returns:
        Tuple of (name, description, raw_frontmatter).
        Name/description default to empty string if not found.
    """
    try:
        content = skill_md_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "", "", None

    frontmatter = parse_frontmatter(content)

    if frontmatter is None:
        return "", "", None

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")

    if isinstance(name, str):
        name = name.strip()
    else:
        name = ""

    if isinstance(description, str):
        description = " ".join(description.split())
    else:
        description = ""

    return name, description, frontmatter


def find_skills(root: Path) -> list[DiscoveredSkill]:
    """Find all skills recursively under a root directory.

    Args:
        root: Root directory to search.

    Returns:
        List of discovered skills.
    """
    skills = []
    root = root.resolve()

    if not root.is_dir():
        return skills

    for skill_md in root.rglob("SKILL.md"):
        skill_dir = skill_md.parent
        name, description, frontmatter = extract_skill_info(skill_md)

        if not name:
            name = skill_dir.name

        skills.append(
            DiscoveredSkill(
                path=skill_dir,
                name=name,
                description=description,
                raw_frontmatter=frontmatter,
            )
        )

    return skills


def discover_single(path: Path) -> DiscoveredSkill | None:
    """Discover a single skill at a given path.

    Args:
        path: Path to skill directory (containing SKILL.md).

    Returns:
        Discovered skill, or None if not a valid skill.
    """
    path = path.resolve()
    skill_md = path / "SKILL.md"

    if not skill_md.exists():
        return None

    name, description, frontmatter = extract_skill_info(skill_md)

    if not name:
        name = path.name

    return DiscoveredSkill(
        path=path,
        name=name,
        description=description,
        raw_frontmatter=frontmatter,
    )
