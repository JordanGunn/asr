"""Copilot adapter for generating GitHub Copilot integration files.

GitHub Copilot supports three types of custom content:
1. Prompt files (.github/prompts/*.prompt.md) - Invokable via /name in chat
2. Instructions file (.github/copilot-instructions.md) - Auto-injected repo-wide rules
3. Scoped instructions (.github/instructions/*.instructions.md) - Path-specific rules

This adapter generates:
- Per-skill prompt files for invokable workflows (/skill-name)
- A consolidated instructions file listing available skills
"""

from pathlib import Path

from adapters.base import BaseAdapter, SkillInfo


class CopilotAdapter(BaseAdapter):
    """Adapter for generating GitHub Copilot files.

    Generates:
    - .github/prompts/{skill}.prompt.md - Invokable via /{skill} in chat
    - .github/copilot-instructions.md - Repository-wide skill index (auto-injected)
    """

    target_name = "copilot"
    target_subdir = ".github/prompts"

    MARKER = "<!-- ASR-MANAGED-SKILLS -->"
    MARKER_END = "<!-- /ASR-MANAGED-SKILLS -->"

    def generate(
        self, skill: SkillInfo, output_dir: Path, copy: bool = False, base_output_dir: Path | None = None
    ) -> Path:
        """Generate a prompt file for a single skill.

        Args:
            skill: Skill information.
            output_dir: Resolved output directory (.github/prompts/).
            copy: If True, use relative paths to local skill copies.
            base_output_dir: Base output directory (for computing relative paths).

        Returns:
            Path to the generated prompt file.
        """
        output_file = output_dir / f"{skill.name}.prompt.md"

        skill_path = self.get_skill_path(skill, base_output_dir or output_dir.parent.parent, copy)

        content = f"""# {skill.name}

{skill.description}

This prompt delegates to the agent skill at `{skill_path}/`.

## Skill Location

- **Path:** `{skill_path}/`
- **Manifest:** `{skill_path}/SKILL.md`

## Usage

Invoke this skill by typing `/{skill.name}` in the Copilot chat.
"""

        output_file.write_text(content, encoding="utf-8")
        return output_file

    def cleanup_stale(self, output_dir: Path, valid_names: set[str]) -> list[Path]:
        """Remove stale Copilot prompt files.

        Args:
            output_dir: Output directory to clean (.github/prompts/).
            valid_names: Set of valid skill names (files to keep).

        Returns:
            List of removed file paths.
        """
        removed = []

        if not output_dir.is_dir():
            return removed

        for file in output_dir.glob("*.prompt.md"):
            name = file.stem.replace(".prompt", "")

            if name in valid_names:
                continue

            try:
                content = file.read_text(encoding="utf-8")
                if "This prompt delegates to the agent skill at" in content:
                    file.unlink()
                    removed.append(file)
            except (OSError, UnicodeDecodeError):
                pass

        return removed

    def generate_all(
        self,
        skills: list[SkillInfo],
        output_dir: Path,
        exclude: set[str] | None = None,
        copy: bool = False,
    ) -> tuple[list[Path], list[Path]]:
        """Generate prompt files and update instructions file.

        Args:
            skills: List of skills to include.
            output_dir: Base output directory.
            exclude: Set of skill names to exclude.
            copy: If True, copy skills locally and use relative paths.

        Returns:
            Tuple of (generated files, removed stale files).
        """
        exclude = exclude or set()

        # Generate prompt files in .github/prompts/
        prompts_dir = self.resolve_output_dir(output_dir)
        prompts_dir.mkdir(parents=True, exist_ok=True)

        active_skills = [s for s in skills if s.name not in exclude]

        # Copy skills if requested
        if copy:
            skills_dir = self.get_skills_dir(output_dir)
            skills_dir.mkdir(parents=True, exist_ok=True)
            for skill in active_skills:
                self.copy_skill(skill, skills_dir)

        generated = []
        valid_names = set()

        for skill in active_skills:
            valid_names.add(skill.name)
            path = self.generate(skill, prompts_dir, copy=copy, base_output_dir=output_dir)
            generated.append(path)

        removed = self.cleanup_stale(prompts_dir, valid_names)

        # Update .github/copilot-instructions.md with skill index
        github_dir = prompts_dir.parent  # .github/
        instructions_file = github_dir / "copilot-instructions.md"

        if active_skills:
            self._update_instructions_file(instructions_file, active_skills)
            generated.append(instructions_file)
        elif instructions_file.exists():
            self._remove_managed_section(instructions_file)

        return generated, removed

    def _update_instructions_file(self, file_path: Path, skills: list[SkillInfo]) -> None:
        """Update or create the copilot-instructions.md file."""
        skills_content = self._build_skills_section(skills)

        if file_path.exists():
            self._update_managed_section(file_path, skills_content)
        else:
            content = f"""# Copilot Instructions

{self.MARKER}
{skills_content}
{self.MARKER_END}
"""
            file_path.write_text(content, encoding="utf-8")

    def _build_skills_section(self, skills: list[SkillInfo]) -> str:
        """Build the managed skills section content."""
        lines = ["## Available Skills", ""]
        lines.append("The following agent skills are available. Invoke them by typing `/<skill-name>` in chat.")
        lines.append("")

        for skill in sorted(skills, key=lambda s: s.name):
            desc = skill.description or "(no description)"
            lines.append(f"- **/{skill.name}** — {desc}")

        lines.append("")
        return "\n".join(lines)

    def _update_managed_section(self, file_path: Path, new_content: str) -> None:
        """Update the managed section in an existing file."""
        content = file_path.read_text(encoding="utf-8")

        start_idx = content.find(self.MARKER)
        end_idx = content.find(self.MARKER_END)

        if start_idx != -1 and end_idx != -1:
            before = content[:start_idx]
            after = content[end_idx + len(self.MARKER_END) :]
            new_full = f"{before}{self.MARKER}\n{new_content}\n{self.MARKER_END}{after}"
        else:
            new_full = f"{content.rstrip()}\n\n{self.MARKER}\n{new_content}\n{self.MARKER_END}\n"

        file_path.write_text(new_full, encoding="utf-8")

    def _remove_managed_section(self, file_path: Path) -> None:
        """Remove the managed section from an existing file."""
        content = file_path.read_text(encoding="utf-8")

        start_idx = content.find(self.MARKER)
        end_idx = content.find(self.MARKER_END)

        if start_idx != -1 and end_idx != -1:
            before = content[:start_idx].rstrip()
            after = content[end_idx + len(self.MARKER_END) :].lstrip()
            new_content = f"{before}\n{after}".strip() + "\n"
            file_path.write_text(new_content, encoding="utf-8")
