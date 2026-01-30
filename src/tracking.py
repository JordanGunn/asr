"""Skill tracking via metadata.oasr frontmatter injection.

This module handles injecting and extracting tracking metadata in SKILL.md files.
Tracking metadata is stored under the `metadata.oasr` field to comply with the
Open Agent Skill specification.
"""

from datetime import datetime, timezone
from pathlib import Path

import yaml


def inject_metadata(skill_path: Path, content_hash: str, source: str) -> bool:
    """Inject tracking metadata into SKILL.md frontmatter.

    Args:
        skill_path: Path to skill directory
        content_hash: SHA256 hash of the skill content
        source: Source path or URL of the skill

    Returns:
        True if metadata was injected, False if SKILL.md not found or injection failed

    Raises:
        OSError: If file cannot be read or written (permission, encoding issues)
    """
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False

    try:
        content = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise OSError(f"Failed to read {skill_md}: {e}") from e

    # Parse existing frontmatter
    frontmatter, body = _split_frontmatter(content)

    if frontmatter is None:
        # No frontmatter exists - shouldn't happen for valid skills, but handle it
        return False

    # Validate frontmatter is a dict
    if not isinstance(frontmatter, dict):
        return False

    # Ensure metadata field exists
    if "metadata" not in frontmatter:
        frontmatter["metadata"] = {}
    elif not isinstance(frontmatter["metadata"], dict):
        # metadata exists but is not a dict - fix it
        frontmatter["metadata"] = {}

    # Inject oasr tracking metadata
    frontmatter["metadata"]["oasr"] = {
        "hash": content_hash,
        "source": str(source),
        "synced": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    # Write back
    try:
        new_content = _serialize_frontmatter(frontmatter) + body
        skill_md.write_text(new_content, encoding="utf-8")
    except (OSError, UnicodeEncodeError) as e:
        raise OSError(f"Failed to write {skill_md}: {e}") from e

    return True


def extract_metadata(skill_path: Path) -> dict | None:
    """Extract tracking metadata from SKILL.md.

    Args:
        skill_path: Path to skill directory

    Returns:
        Dictionary with 'hash', 'source', 'synced' keys, or None if not tracked
        Returns None on any error (file not found, encoding issues, corrupted metadata)
    """
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return None

    try:
        content = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        # Cannot read file - treat as untracked
        return None

    frontmatter, _ = _split_frontmatter(content)

    if frontmatter is None or not isinstance(frontmatter, dict):
        return None

    # Safely extract metadata.oasr
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        return None

    oasr = metadata.get("oasr")
    if not isinstance(oasr, dict):
        return None

    # Validate required fields
    if "hash" not in oasr or "source" not in oasr:
        return None

    return oasr


def strip_tracking_metadata(frontmatter: dict) -> dict:
    """Remove metadata.oasr from frontmatter dictionary.

    This is used when comparing registry skills to avoid flagging
    tracking metadata as drift.

    Args:
        frontmatter: Frontmatter dictionary

    Returns:
        Copy of frontmatter with metadata.oasr removed
    """
    import copy

    cleaned = copy.deepcopy(frontmatter)

    if "metadata" in cleaned and isinstance(cleaned["metadata"], dict):
        cleaned["metadata"].pop("oasr", None)
        # Remove metadata field entirely if it's now empty
        if not cleaned["metadata"]:
            cleaned.pop("metadata")

    return cleaned


def _split_frontmatter(content: str) -> tuple[dict | None, str]:
    """Split markdown content into frontmatter and body.

    Args:
        content: Full markdown content

    Returns:
        Tuple of (frontmatter_dict, body_text)
    """
    if not content.startswith("---"):
        return None, content

    lines = content.split("\n")
    end_idx = None

    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None, content

    frontmatter_text = "\n".join(lines[1:end_idx])
    body_text = "\n".join(lines[end_idx + 1 :])

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        return frontmatter, body_text
    except yaml.YAMLError:
        return None, content


def _serialize_frontmatter(frontmatter: dict) -> str:
    """Serialize frontmatter dictionary back to YAML with delimiters.

    Args:
        frontmatter: Frontmatter dictionary

    Returns:
        YAML string with --- delimiters
    """
    yaml_str = yaml.safe_dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return f"---\n{yaml_str}---\n"
