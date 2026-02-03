"""Codex agent driver."""

from pathlib import Path

from agents.base import AgentDriver


class CodexDriver(AgentDriver):
    """Driver for Codex CLI agent."""

    def get_name(self) -> str:
        """Get the agent name."""
        return "codex"

    def get_binary_name(self) -> str:
        """Get the CLI binary name."""
        return "codex"

    def build_command(
        self,
        skill_content: str,
        user_prompt: str,
        cwd: Path,
        extra_args: list[str] | None = None,
    ) -> list[str]:
        """Build codex exec command.

        Codex syntax: codex exec "<prompt>"
        """
        injected_prompt = self.format_injected_prompt(skill_content, user_prompt, cwd)
        cmd = ["codex", "exec"]
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(injected_prompt)
        return cmd
