"""Base adapter interface for generating IDE-specific skill files."""

from abc import ABC, abstractmethod
from pathlib import Path
import shutil
from typing import Protocol


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
    def generate(self, skill: SkillInfo, output_dir: Path, copy: bool = False, base_output_dir: Path | None = None) -> Path:
        """Generate IDE-specific file for a skill.
        
        Args:
            skill: Skill information.
            output_dir: Resolved output directory for adapter files.
            copy: If True, use relative paths to local skill copies.
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
    
    def copy_skill(self, skill: SkillInfo, skills_dir: Path) -> Path:
        """Copy a skill to the local skills directory.
        
        Args:
            skill: Skill to copy.
            skills_dir: Target skills directory.
        
        Returns:
            Path to the copied skill directory.
        """
        src = Path(skill.path)
        dest = skills_dir / skill.name
        
        if dest.exists():
            shutil.rmtree(dest)
        
        shutil.copytree(src, dest)
        return dest
    
    def get_skill_path(self, skill: SkillInfo, output_dir: Path, copy: bool = False) -> str:
        """Get the skill path to use in generated files.
        
        Args:
            skill: Skill information.
            output_dir: Base output directory.
            copy: If True, return relative path to local copy.
        
        Returns:
            Path string to use in adapter output.
        """
        if copy:
            # Return relative path from adapter output to skills dir
            # e.g., "../skills/my-skill" from .windsurf/workflows/
            return f"../skills/{skill.name}"
        return skill.path
    
    def generate_all(
        self,
        skills: list[SkillInfo],
        output_dir: Path,
        exclude: set[str] | None = None,
        copy: bool = False,
    ) -> tuple[list[Path], list[Path]]:
        """Generate files for all skills and cleanup stale ones.
        
        Args:
            skills: List of skills to generate.
            output_dir: Base output directory.
            exclude: Set of skill names to exclude.
            copy: If True, copy skills locally and use relative paths.
        
        Returns:
            Tuple of (generated files, removed stale files).
        """
        exclude = exclude or set()
        resolved_dir = self.resolve_output_dir(output_dir)
        resolved_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy skills if requested
        if copy:
            skills_dir = self.get_skills_dir(output_dir)
            skills_dir.mkdir(parents=True, exist_ok=True)
            for skill in skills:
                if skill.name not in exclude:
                    self.copy_skill(skill, skills_dir)
        
        generated = []
        valid_names = set()
        
        for skill in skills:
            if skill.name in exclude:
                continue
            
            valid_names.add(skill.name)
            path = self.generate(skill, resolved_dir, copy=copy, base_output_dir=output_dir)
            generated.append(path)
        
        removed = self.cleanup_stale(resolved_dir, valid_names)
        
        return generated, removed
