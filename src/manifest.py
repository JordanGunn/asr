"""Skill manifest management for auditing and verification.

Manifests track the state of registered skills, enabling:
- Source verification (content hashing)
- Change detection (modified files)
- Existence validation (missing sources)
- Audit trails (registration timestamps)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal


MANIFESTS_DIR = "manifests"
MANIFEST_SUFFIX = ".manifest.json"
MANIFEST_VERSION = 1


@dataclass
class FileEntry:
    """A single file in the manifest."""
    path: str
    hash: str
    size: int
    
    def to_dict(self) -> dict:
        return {"path": self.path, "hash": self.hash, "size": self.size}
    
    @classmethod
    def from_dict(cls, data: dict) -> FileEntry:
        return cls(path=data["path"], hash=data["hash"], size=data["size"])


@dataclass
class SkillManifest:
    """Manifest for a registered skill."""
    name: str
    source_path: str
    description: str
    registered_at: str
    content_hash: str
    files: list[FileEntry] = field(default_factory=list)
    version: int = MANIFEST_VERSION
    
    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "name": self.name,
            "source_path": self.source_path,
            "description": self.description,
            "registered_at": self.registered_at,
            "content_hash": self.content_hash,
            "files": [f.to_dict() for f in self.files],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> SkillManifest:
        return cls(
            version=data.get("version", 1),
            name=data["name"],
            source_path=data["source_path"],
            description=data["description"],
            registered_at=data["registered_at"],
            content_hash=data["content_hash"],
            files=[FileEntry.from_dict(f) for f in data.get("files", [])],
        )


SkillStatus = Literal["valid", "modified", "missing", "orphaned", "untracked"]


@dataclass
class ManifestStatus:
    """Status of a skill manifest check."""
    name: str
    status: SkillStatus
    source_path: str | None = None
    message: str = ""
    changed_files: list[str] = field(default_factory=list)
    added_files: list[str] = field(default_factory=list)
    removed_files: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "source_path": self.source_path,
            "message": self.message,
            "changed_files": self.changed_files,
            "added_files": self.added_files,
            "removed_files": self.removed_files,
        }


def hash_file(path: Path) -> str:
    """Compute SHA256 hash of a file.
    
    Args:
        path: Path to the file.
    
    Returns:
        Hash string in format "sha256:<hex>".
    """
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return f"sha256:{hasher.hexdigest()}"
    except (OSError, IOError):
        return "sha256:error"


def hash_directory(path: Path) -> tuple[str, list[FileEntry]]:
    """Compute content hash of a directory.
    
    Creates a deterministic hash based on all file paths and their contents.
    
    Args:
        path: Path to the directory.
    
    Returns:
        Tuple of (content_hash, list of FileEntry).
    """
    entries = []
    hasher = hashlib.sha256()
    
    if not path.is_dir():
        return "sha256:missing", []
    
    files = sorted(path.rglob("*"))
    
    for file_path in files:
        if file_path.is_file():
            rel_path = str(file_path.relative_to(path))
            file_hash = hash_file(file_path)
            file_size = file_path.stat().st_size
            
            entries.append(FileEntry(
                path=rel_path,
                hash=file_hash,
                size=file_size,
            ))
            
            hasher.update(rel_path.encode("utf-8"))
            hasher.update(file_hash.encode("utf-8"))
    
    return f"sha256:{hasher.hexdigest()}", entries


def get_manifests_dir(config_dir: Path | None = None) -> Path:
    """Get the manifests directory path.
    
    Args:
        config_dir: Override config directory (default: ~/.skills).
    
    Returns:
        Path to manifests directory.
    """
    if config_dir is None:
        config_dir = Path.home() / ".skills"
    return config_dir / MANIFESTS_DIR


def create_manifest(
    name: str,
    source_path: Path,
    description: str,
) -> SkillManifest:
    """Create a new manifest for a skill.
    
    Args:
        name: Skill name.
        source_path: Absolute path to skill directory.
        description: Skill description.
    
    Returns:
        New SkillManifest instance.
    """
    content_hash, files = hash_directory(source_path)
    
    return SkillManifest(
        name=name,
        source_path=str(source_path),
        description=description,
        registered_at=datetime.now(timezone.utc).isoformat(),
        content_hash=content_hash,
        files=files,
    )


def save_manifest(manifest: SkillManifest, config_dir: Path | None = None) -> Path:
    """Save a manifest to disk.
    
    Args:
        manifest: Manifest to save.
        config_dir: Override config directory.
    
    Returns:
        Path to saved manifest file.
    """
    manifests_dir = get_manifests_dir(config_dir)
    manifests_dir.mkdir(parents=True, exist_ok=True)
    
    manifest_path = manifests_dir / f"{manifest.name}{MANIFEST_SUFFIX}"
    manifest_path.write_text(
        json.dumps(manifest.to_dict(), indent=2),
        encoding="utf-8",
    )
    
    return manifest_path


def load_manifest(name: str, config_dir: Path | None = None) -> SkillManifest | None:
    """Load a manifest from disk.
    
    Args:
        name: Skill name.
        config_dir: Override config directory.
    
    Returns:
        SkillManifest if found, None otherwise.
    """
    manifests_dir = get_manifests_dir(config_dir)
    manifest_path = manifests_dir / f"{name}{MANIFEST_SUFFIX}"
    
    if not manifest_path.is_file():
        return None
    
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return SkillManifest.from_dict(data)
    except (json.JSONDecodeError, KeyError, OSError):
        return None


def delete_manifest(name: str, config_dir: Path | None = None) -> bool:
    """Delete a manifest from disk.
    
    Args:
        name: Skill name.
        config_dir: Override config directory.
    
    Returns:
        True if deleted, False if not found.
    """
    manifests_dir = get_manifests_dir(config_dir)
    manifest_path = manifests_dir / f"{name}{MANIFEST_SUFFIX}"
    
    if manifest_path.is_file():
        manifest_path.unlink()
        return True
    return False


def list_manifests(config_dir: Path | None = None) -> list[str]:
    """List all manifest names.
    
    Args:
        config_dir: Override config directory.
    
    Returns:
        List of skill names with manifests.
    """
    manifests_dir = get_manifests_dir(config_dir)
    
    if not manifests_dir.is_dir():
        return []
    
    names = []
    for path in manifests_dir.glob(f"*{MANIFEST_SUFFIX}"):
        name = path.name[:-len(MANIFEST_SUFFIX)]
        names.append(name)
    
    return sorted(names)


def check_manifest(manifest: SkillManifest) -> ManifestStatus:
    """Check if a manifest matches its source.
    
    Args:
        manifest: Manifest to check.
    
    Returns:
        ManifestStatus with validation results.
    """
    source_path = Path(manifest.source_path)
    
    if not source_path.exists():
        return ManifestStatus(
            name=manifest.name,
            status="missing",
            source_path=manifest.source_path,
            message=f"Source path no longer exists: {manifest.source_path}",
        )
    
    current_hash, current_files = hash_directory(source_path)
    
    if current_hash == manifest.content_hash:
        return ManifestStatus(
            name=manifest.name,
            status="valid",
            source_path=manifest.source_path,
            message="Source matches manifest",
        )
    
    current_file_map = {f.path: f for f in current_files}
    manifest_file_map = {f.path: f for f in manifest.files}
    
    changed = []
    added = []
    removed = []
    
    for path, entry in current_file_map.items():
        if path not in manifest_file_map:
            added.append(path)
        elif entry.hash != manifest_file_map[path].hash:
            changed.append(path)
    
    for path in manifest_file_map:
        if path not in current_file_map:
            removed.append(path)
    
    return ManifestStatus(
        name=manifest.name,
        status="modified",
        source_path=manifest.source_path,
        message=f"Source modified: {len(changed)} changed, {len(added)} added, {len(removed)} removed",
        changed_files=changed,
        added_files=added,
        removed_files=removed,
    )


def sync_manifest(manifest: SkillManifest, config_dir: Path | None = None) -> SkillManifest:
    """Update a manifest to match current source state.
    
    Args:
        manifest: Existing manifest.
        config_dir: Override config directory.
    
    Returns:
        Updated manifest (also saved to disk).
    """
    source_path = Path(manifest.source_path)
    content_hash, files = hash_directory(source_path)
    
    updated = SkillManifest(
        name=manifest.name,
        source_path=manifest.source_path,
        description=manifest.description,
        registered_at=manifest.registered_at,
        content_hash=content_hash,
        files=files,
    )
    
    save_manifest(updated, config_dir)
    return updated
