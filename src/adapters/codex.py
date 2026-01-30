"""Codex adapter for generating codex skill files.

Note: Codex format is TBD. Currently uses same format as Cursor.
"""

from pathlib import Path

from adapters.base import BaseAdapter, SkillInfo


class CodexAdapter(BaseAdapter):
    """Adapter for generating Codex skill files.

    Placeholder implementation - uses same format as Cursor commands.
    """

    target_name = "codex"
    target_subdir = ".codex/skills"

    def generate(
        self, skill: SkillInfo, output_dir: Path, copy: bool = False, base_output_dir: Path | None = None
    ) -> Path:
        """Generate a Codex skill file for a skill.

        Args:
            skill: Skill information.
            output_dir: Resolved output directory (.codex/skills/).
            copy: If True, use relative paths to local skill copies.
            base_output_dir: Base output directory (for computing relative paths).

        Returns:
            Path to the generated file.
        """
        output_file = output_dir / f"{skill.name}.md"

        skill_path = self.get_skill_path(skill, base_output_dir or output_dir.parent.parent, copy)

        content = f"""# {skill.name}

{skill.description}

This skill delegates to the agent skill at `{skill_path}/`.

## Skill Location

- **Path:** `{skill_path}/`
- **Manifest:** `{skill_path}/SKILL.md`
"""

        output_file.write_text(content, encoding="utf-8")
        return output_file

    def cleanup_stale(self, output_dir: Path, valid_names: set[str]) -> list[Path]:
        """Remove stale Codex skill files.

        Only removes files that look like generated skill files.

        Args:
            output_dir: Output directory to clean.
            valid_names: Set of valid skill names (files to keep).

        Returns:
            List of removed file paths.
        """
        removed = []

        if not output_dir.is_dir():
            return removed

        for file in output_dir.glob("*.md"):
            name = file.stem

            if name in valid_names:
                continue

            try:
                content = file.read_text(encoding="utf-8")
                if "This skill delegates to the agent skill at" in content:
                    file.unlink()
                    removed.append(file)
            except (OSError, UnicodeDecodeError):
                pass

        return removed
