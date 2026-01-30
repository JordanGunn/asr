"""Registry management for ~/.oasr/registry.toml."""

import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w

from config import OASR_DIR, ensure_skills_dir
from manifest import create_manifest, delete_manifest, save_manifest

REGISTRY_FILE = OASR_DIR / "registry.toml"


@dataclass
class SkillEntry:
    """A registered skill entry."""

    path: str
    name: str
    description: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary for TOML serialization."""
        return {
            "path": self.path,
            "name": self.name,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "SkillEntry":
        """Create from dictionary."""
        return cls(
            path=data.get("path", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
        )


def load_registry(registry_path: Path | None = None) -> list[SkillEntry]:
    """Load registry from TOML file.

    Args:
        registry_path: Override registry file path. Defaults to ~/.oasr/registry.toml.

    Returns:
        List of registered skill entries.
    """
    path = registry_path or REGISTRY_FILE

    if not path.exists():
        return []

    with open(path, "rb") as f:
        data = tomllib.load(f)

    skills = data.get("skill", [])
    return [SkillEntry.from_dict(s) for s in skills]


def save_registry(entries: list[SkillEntry], registry_path: Path | None = None) -> None:
    """Save registry to TOML file.

    Args:
        entries: List of skill entries to save.
        registry_path: Override registry file path. Defaults to ~/.skills/registry.toml.
    """
    path = registry_path or REGISTRY_FILE
    ensure_skills_dir()

    data = {"skill": [e.to_dict() for e in entries]}

    with open(path, "wb") as f:
        tomli_w.dump(data, f)


def add_skill(
    entry: SkillEntry,
    registry_path: Path | None = None,
    create_manifest_artifact: bool = True,
) -> bool:
    """Add or update a skill in the registry.

    Args:
        entry: Skill entry to add.
        registry_path: Override registry file path.
        create_manifest_artifact: Whether to create/update the manifest artifact.

    Returns:
        True if skill was added, False if it was updated (already existed).
    """
    entries = load_registry(registry_path)
    is_new = True

    for i, existing in enumerate(entries):
        if existing.name == entry.name or existing.path == entry.path:
            entries[i] = entry
            is_new = False
            break

    if is_new:
        entries.append(entry)

    save_registry(entries, registry_path)

    if create_manifest_artifact:
        manifest = create_manifest(
            name=entry.name,
            source_path=entry.path,  # Keep as string (can be URL or path)
            description=entry.description,
        )
        save_manifest(manifest)

    return is_new


def remove_skill(
    name_or_path: str,
    registry_path: Path | None = None,
    delete_manifest_artifact: bool = True,
) -> bool:
    """Remove a skill from the registry by name or path.

    Args:
        name_or_path: Skill name or path to remove.
        registry_path: Override registry file path.
        delete_manifest_artifact: Whether to delete the manifest artifact.

    Returns:
        True if skill was removed, False if not found.
    """
    entries = load_registry(registry_path)
    removed_name = None

    new_entries = []
    for e in entries:
        if e.name == name_or_path or e.path == name_or_path:
            removed_name = e.name
        else:
            new_entries.append(e)

    if removed_name:
        save_registry(new_entries, registry_path)
        if delete_manifest_artifact:
            delete_manifest(removed_name)
        return True

    return False


def find_skill(name_or_path: str, registry_path: Path | None = None) -> SkillEntry | None:
    """Find a skill by name or path.

    Args:
        name_or_path: Skill name or path to find.
        registry_path: Override registry file path.

    Returns:
        Skill entry if found, None otherwise.
    """
    entries = load_registry(registry_path)

    for entry in entries:
        if entry.name == name_or_path or entry.path == name_or_path:
            return entry

    return None
