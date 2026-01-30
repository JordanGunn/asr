"""Windsurf adapter for generating .windsurf/workflows/*.md files."""

import json
from pathlib import Path

from adapters.base import BaseAdapter, SkillInfo


class WindsurfAdapter(BaseAdapter):
    """Adapter for generating Windsurf workflow files."""

    target_name = "windsurf"
    target_subdir = ".windsurf/workflows"

    def generate(
        self, skill: SkillInfo, output_dir: Path, copy: bool = False, base_output_dir: Path | None = None
    ) -> Path:
        """Generate a Windsurf workflow file for a skill.

        Args:
            skill: Skill information.
            output_dir: Resolved output directory (.windsurf/workflows/).
            copy: If True, use relative paths to local skill copies.
            base_output_dir: Base output directory (for computing relative paths).

        Returns:
            Path to the generated file.
        """
        output_file = output_dir / f"{skill.name}.md"

        skill_path = self.get_skill_path(skill, base_output_dir or output_dir.parent.parent, copy)
        desc_yaml = json.dumps(skill.description)

        content = f"""---
description: {desc_yaml}
auto_execution_mode: 1
---

# {skill.name}

This workflow delegates to the agent skill at `{skill_path}/`.

## Skill Location

- **Path:** `{skill_path}/`
- **Manifest:** `{skill_path}/SKILL.md`
"""

        output_file.write_text(content, encoding="utf-8")
        return output_file

    def cleanup_stale(self, output_dir: Path, valid_names: set[str]) -> list[Path]:
        """Remove stale Windsurf workflow files.

        Only removes files that look like generated skill workflows.

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
                if "This workflow delegates to the agent skill at" in content:
                    file.unlink()
                    removed.append(file)
            except (OSError, UnicodeDecodeError):
                pass

        return removed
