"""Base adapter interface for generating IDE-specific skill files."""

import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Protocol

from skillcopy import copy_skill as copy_skill_unified


class SkillInfo(Protocol):
    """Protocol for skill information."""

    path: str
    name: str
    description: str


class BaseAdapter(ABC):
    """Abstract base class for adapters."""

    target_name: str = ""
    target_subdir: str = ""

    def resolve_output_dir(self, output_dir: Path) -> Path:
        """Resolve the actual output directory based on smart path detection.

        If output_dir ends with the target subdir pattern, use it directly.
        Otherwise, append the target subdir.

        Args:
            output_dir: User-specified output directory.

        Returns:
            Resolved output directory path.
        """
        output_str = str(output_dir)

        if output_str.endswith(self.target_subdir):
            return output_dir

        base_dir = self.target_subdir.rsplit("/", 1)[0]
        if output_str.endswith(base_dir):
            subdir_name = self.target_subdir.rsplit("/", 1)[1]
            return output_dir / subdir_name

        return output_dir / self.target_subdir

    @abstractmethod
    def generate(
        self, skill: SkillInfo, output_dir: Path, copy: bool = True, base_output_dir: Path | None = None
    ) -> Path:
        """Generate IDE-specific file for a skill.

        Args:
            skill: Skill information.
            output_dir: Resolved output directory for adapter files.
            copy: Always True (kept for backward compatibility).
            base_output_dir: Base output directory (for computing relative paths).

        Returns:
            Path to the generated file.
        """
        pass

    @abstractmethod
    def cleanup_stale(self, output_dir: Path, valid_names: set[str]) -> list[Path]:
        """Remove stale generated files.

        Args:
            output_dir: Output directory to clean.
            valid_names: Set of valid skill names (files to keep).

        Returns:
            List of removed file paths.
        """
        pass

    def get_skills_dir(self, output_dir: Path) -> Path:
        """Get the skills directory path for this adapter.

        Returns the sibling skills/ directory relative to the adapter output.
        E.g., for .windsurf/workflows/, returns .windsurf/skills/

        Args:
            output_dir: Base output directory.

        Returns:
            Path to the skills directory.
        """
        base = self.target_subdir.split("/")[0]  # e.g., ".windsurf" or ".github"
        return output_dir / base / "skills"

    def copy_skill(self, skill: SkillInfo, skills_dir: Path, show_progress: bool = False) -> Path:
        """Copy a skill to the local skills directory with tracking metadata.

        Uses unified copy interface (handles both local and remote).

        Args:
            skill: Skill to copy.
            skills_dir: Target skills directory.
            show_progress: If True, show progress for remote skills

        Returns:
            Path to the copied skill directory.
        """
        dest = skills_dir / skill.name

        # Get the skill's content hash from manifest for tracking
        # If manifest doesn't exist, skip tracking (graceful degradation)
        inject_tracking = False
        source_hash = None

        try:
            from manifest import load_manifest

            manifest = load_manifest(skill.name)
            if manifest:
                source_hash = manifest.content_hash
                inject_tracking = True
        except Exception:
            # Gracefully skip tracking if manifest cannot be loaded
            pass

        return copy_skill_unified(
            skill.path,
            dest,
            validate=False,
            show_progress=show_progress,
            skill_name=skill.name,
            inject_tracking=inject_tracking,
            source_hash=source_hash,
        )

    def get_skill_path(self, skill: SkillInfo, output_dir: Path, copy: bool = True) -> str:
        """Get the skill path to use in generated files.

        Args:
            skill: Skill information.
            output_dir: Base output directory.
            copy: Always True (skills are always copied now).

        Returns:
            Relative path string to use in adapter output.
        """
        # Always return relative path to local copy
        return f"../skills/{skill.name}"

    def generate_all(
        self,
        skills: list[SkillInfo],
        output_dir: Path,
        exclude: set[str] | None = None,
        copy: bool = True,  # Always True, kept for backward compatibility
    ) -> tuple[list[Path], list[Path]]:
        """Generate files for all skills and cleanup stale ones.

        Args:
            skills: List of skills to generate.
            output_dir: Base output directory.
            exclude: Set of skill names to exclude.
            copy: Always True (kept for backward compatibility).

        Returns:
            Tuple of (generated files, removed stale files).
        """
        exclude = exclude or set()
        resolved_dir = self.resolve_output_dir(output_dir)
        resolved_dir.mkdir(parents=True, exist_ok=True)

        # Always copy skills (handles both local and remote)
        skills_dir = self.get_skills_dir(output_dir)
        skills_dir.mkdir(parents=True, exist_ok=True)

        # Separate remote and local skills
        from skillcopy.remote import is_remote_source

        remote_skills = [(s, skills_dir / s.name) for s in skills if s.name not in exclude and is_remote_source(s.path)]
        local_skills = [
            (s, skills_dir / s.name) for s in skills if s.name not in exclude and not is_remote_source(s.path)
        ]

        failed_skills = []

        # Copy remote skills in parallel
        if remote_skills:
            print(f"\nCopying {len(remote_skills)} remote skill(s)...", file=sys.stderr)
            import threading
            from concurrent.futures import ThreadPoolExecutor, as_completed

            # Thread-safe print lock
            print_lock = threading.Lock()

            def copy_remote_with_progress(skill, dest):
                """Copy a remote skill with thread-safe progress output."""
                try:
                    with print_lock:
                        platform = (
                            "GitHub"
                            if "github.com" in skill.path
                            else "GitLab"
                            if "gitlab.com" in skill.path
                            else "remote"
                        )
                        print(f"  ↓ {skill.name} (fetching from {platform}...)", file=sys.stderr, flush=True)

                    self.copy_skill(skill, skills_dir, show_progress=False)  # We handle progress here

                    with print_lock:
                        print(f"  ✓ {skill.name} (downloaded)", file=sys.stderr)

                    return skill.name, True, None
                except Exception as e:
                    with print_lock:
                        print(f"  ✗ {skill.name} ({str(e)[:50]}...)", file=sys.stderr)
                    return skill.name, False, str(e)

            # Fetch remote skills in parallel (max 4 concurrent)
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(copy_remote_with_progress, skill, dest): skill.name for skill, dest in remote_skills
                }

                for future in as_completed(futures):
                    skill_name, success, error = future.result()
                    if not success:
                        failed_skills.append(skill_name)

        # Copy local skills sequentially (fast anyway)
        for skill, _dest in local_skills:
            try:
                self.copy_skill(skill, skills_dir, show_progress=False)
            except Exception as e:
                print(f"⚠ Warning: Failed to copy {skill.name}: {e}", file=sys.stderr)
                failed_skills.append(skill.name)

        generated = []
        valid_names = set()

        for skill in skills:
            if skill.name in exclude:
                continue

            # Skip skills that failed to copy
            if skill.name in failed_skills:
                continue

            valid_names.add(skill.name)
            path = self.generate(skill, resolved_dir, copy=True, base_output_dir=output_dir)
            generated.append(path)

        removed = self.cleanup_stale(resolved_dir, valid_names)

        return generated, removed
