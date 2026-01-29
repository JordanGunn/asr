"""Reference manifest for 'use' OASR Skill

After a User uses the 'use' command to copy an ASR Skill into their project, a
manifest file is created to track the source and version of the Skill.
This manifest is stored in the OASR's .skills/manifests/ directory.
When the User later runs 'sync' in their project, the manifest is
consulted to determine if the Skill needs to be updated from its source.

Manifest track the source and version of an ASR Skill copied into a project.
Fields:
- name: Name of the skill
- clones: List of SkillClone entries
- manifest_version: Version of the manifest format

Each SkillClone entry contains:
- clone: Path to the cloned skill
- hash: Version hash of the skill
- first_cloned: Timestamp of first clone
- last_synced: Timestamp of last sync

When 'sync' is run, the manifest is checked to see if the skill has changed
at its source. If so, the skill is updated in the project and the manifest is updated
with the new hash and last_synced timestamp.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# Store per-project clone manifests under a `.skills/manifests` directory by default.
MANIFESTS_DIR = ".skills/manifests"
CLONE_MANIFEST_SUFFIX = "clones.manifest.json"
MANIFEST_VERSION = 1

@dataclass
class CloneManifest:
    """Manifest tracking a cloned ASR Skill."""
    name: str
    clones: list["SkillClone"]
    manifest_version: int = MANIFEST_VERSION

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "clones": [c.to_dict() for c in self.clones],
            "manifest_version": self.manifest_version,
        }

    @staticmethod
    def from_dict(data: dict) -> "CloneManifest":
        clones = [SkillClone.from_dict(c) for c in data.get("clones", [])]
        return CloneManifest(
            name=data["name"],
            clones=clones,
            manifest_version=data.get("manifest_version", MANIFEST_VERSION),
        )

    @staticmethod
    def load_from_file(manifest_path: Path) -> "CloneManifest":
        with manifest_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return CloneManifest.from_dict(data)

    @staticmethod
    def save_to_file(manifest: "CloneManifest", manifest_path: Path) -> None:
        # Ensure parent dir exists
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest.to_dict(), f, indent=4)



@dataclass
class SkillClone:
    """Information about a cloned ASR Skill."""
    clone: str
    hash: str
    first_cloned: str
    last_synced: str

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "SkillClone":
        return SkillClone(
            clone=data["clone"],
            hash=data["hash"],
            first_cloned=data["first_cloned"],
            last_synced=data["last_synced"],
        )

    def check_version(self, current_hash: str) -> bool:
        return self.hash == current_hash

    def update_version(self, new_hash: str, timestamp: str) -> None:
        self.hash = new_hash
        self.last_synced = timestamp


def compute_skill_hash(skill_path: Path) -> str:
    """Compute a deterministic SHA-256 hash of a skill directory for versioning.

    Returns a string in the format "sha256:<hex>" or "sha256:missing" if the
    provided path is not a directory.
    """
    skill_path = Path(skill_path)
    if not skill_path.exists() or not skill_path.is_dir():
        return "sha256:missing"

    hasher = hashlib.sha256()
    # Walk files in a deterministic order and include relative path in the hash.
    for file_path in sorted(skill_path.rglob("*")):
        if file_path.is_file():
            rel = str(file_path.relative_to(skill_path)).replace("\\", "/")
            hasher.update(rel.encode("utf-8"))
            try:
                with file_path.open("rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        hasher.update(chunk)
            except (OSError, IOError):
                # include a deterministic marker on IO/read error
                hasher.update(b"error")
    return f"sha256:{hasher.hexdigest()}"

def get_manifest_path(skill_name: str) -> Path:
    """Get the path to the clone manifest for a given skill name."""
    manifests_dir = Path(MANIFESTS_DIR)
    manifests_dir.mkdir(parents=True, exist_ok=True)
    return manifests_dir / f"{skill_name}.{CLONE_MANIFEST_SUFFIX}"



def create_clone_manifest(skill_name: str, clone_path: str, skill_hash: str, timestamp: str) -> CloneManifest:
    """Create a new clone manifest for a skill."""
    clone = SkillClone(
        clone=clone_path,
        hash=skill_hash,
        first_cloned=timestamp,
        last_synced=timestamp,
    )
    return CloneManifest(
        name=skill_name,
        clones=[clone],
    )

def update_clone_manifest(manifest: CloneManifest, clone_path: str, skill_hash: str, timestamp: str) -> None:
    """Update an existing clone manifest with new clone information."""
    for c in manifest.clones:
        if c.clone == clone_path:
            c.hash = skill_hash
            c.last_synced = timestamp
            return
    # If clone not found, add a new entry
    new_clone = SkillClone(
        clone=clone_path,
        hash=skill_hash,
        first_cloned=timestamp,
        last_synced=timestamp,
    )
    manifest.clones.append(new_clone)

def save_clone_manifest(skill_name: str, clone_path: str, skill_hash: str, timestamp: str) -> None:
    """Save or update the clone manifest for a skill."""
    manifest_path = get_manifest_path(skill_name)
    if manifest_path.exists():
        manifest = CloneManifest.load_from_file(manifest_path)
        update_clone_manifest(manifest, clone_path, skill_hash, timestamp)
    else:
        manifest = create_clone_manifest(skill_name, clone_path, skill_hash, timestamp)
    CloneManifest.save_to_file(manifest, manifest_path)

def load_clone_manifest(skill_name: str) -> CloneManifest | None:
    """Load the clone manifest for a given skill name."""
    manifest_path = get_manifest_path(skill_name)
    if manifest_path.exists():
        return CloneManifest.load_from_file(manifest_path)
    return None

def check_clone_manifest(manifest: CloneManifest, skill_path: Path) -> bool:
    """Check if the skill at skill_path matches the version in the manifest."""
    current_hash = compute_skill_hash(skill_path)
    for clone in manifest.clones:
        if clone.check_version(current_hash):
            return True
    return False

def add_or_update_clone_entry(skill_name: str, skill_path: Path | str, timestamp: str = None) -> None:
    """Add or update the clone entry for a skill.

    Accept either a Path or str for `skill_path`; the function will convert to
    a `Path` internally.
    """
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat() + "Z"
    skill_path = Path(skill_path)
    manifest = load_clone_manifest(skill_name)
    skill_hash = compute_skill_hash(skill_path)
    if manifest:
        update_clone_manifest(manifest, str(skill_path), skill_hash, timestamp)
    else:
        manifest = create_clone_manifest(skill_name, str(skill_path), skill_hash, timestamp)
    manifest_path = get_manifest_path(skill_name)
    CloneManifest.save_to_file(manifest, manifest_path)

def remove_clone_entry(skill_name: str, skill_path: Path | str) -> None:
    """Remove a clone entry for a skill."""
    manifest = load_clone_manifest(skill_name)
    if not manifest:
        return
    manifest.clones = [c for c in manifest.clones if c.clone != str(skill_path)]
    manifest_path = get_manifest_path(skill_name)
    if manifest.clones:
        CloneManifest.save_to_file(manifest, manifest_path)
    else:
        try:
            if manifest_path.exists():
                manifest_path.unlink()
        except OSError:
            # best-effort removal
            pass


def remove_clone_manifest(skill_name: str) -> None:
    """Delete the clone manifest file for a skill (if present)."""
    manifest_path = get_manifest_path(skill_name)
    try:
        if manifest_path.exists():
            manifest_path.unlink()
    except OSError:
        pass

def update_clone_skill(skill_name: str, skill_path: Path | str, timestamp: str = None) -> None:
    """Used in 'sync' to update the skill clone(s) and manifest.

    If the skill has changed at its source, update each recorded clone directory and update
    the manifest with the new hash and last_synced timestamp.

    This function is best-effort: it will skip problematic clone paths rather than raising.
    """
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat() + "Z"
    skill_path = Path(skill_path)
    manifest = load_clone_manifest(skill_name)
    if not manifest:
        return
    current_hash = compute_skill_hash(skill_path)
    for clone in manifest.clones:
        clone_dest = Path(clone.clone)
        if not clone.check_version(current_hash):
            try:
                # If the destination exists, remove it first. Otherwise create parent and copy.
                if clone_dest.exists():
                    # safety: avoid accidentally deleting filesystem root or empty strings
                    try:
                        resolved = clone_dest.resolve()
                    except Exception:
                        # if resolution fails, skip this clone
                        continue
                    if str(resolved) in ("/", ""):
                        # skip unsafe path
                        continue
                    shutil.rmtree(clone_dest)
                # copy the updated source into place
                shutil.copytree(skill_path, clone_dest)
                clone.update_version(current_hash, timestamp)
            except Exception:
                # best-effort: skip clones that cannot be updated
                continue
    manifest_path = get_manifest_path(skill_name)
    CloneManifest.save_to_file(manifest, manifest_path)
