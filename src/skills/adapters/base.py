"""Base adapter interface for generating IDE-specific skill files."""

from abc import ABC, abstractmethod
from pathlib import Path
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
    def generate(self, skill: SkillInfo, output_dir: Path) -> Path:
        """Generate IDE-specific file for a skill.
        
        Args:
            skill: Skill information.
            output_dir: Base output directory.
        
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
    
    def generate_all(
        self,
        skills: list[SkillInfo],
        output_dir: Path,
        exclude: set[str] | None = None,
    ) -> tuple[list[Path], list[Path]]:
        """Generate files for all skills and cleanup stale ones.
        
        Args:
            skills: List of skills to generate.
            output_dir: Base output directory.
            exclude: Set of skill names to exclude.
        
        Returns:
            Tuple of (generated files, removed stale files).
        """
        exclude = exclude or set()
        resolved_dir = self.resolve_output_dir(output_dir)
        resolved_dir.mkdir(parents=True, exist_ok=True)
        
        generated = []
        valid_names = set()
        
        for skill in skills:
            if skill.name in exclude:
                continue
            
            valid_names.add(skill.name)
            path = self.generate(skill, resolved_dir)
            generated.append(path)
        
        removed = self.cleanup_stale(resolved_dir, valid_names)
        
        return generated, removed
