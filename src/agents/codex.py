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

    def build_command(self, skill_content: str, user_prompt: str, cwd: Path) -> list[str]:
        """Build codex exec command.

        Codex syntax: codex exec "<prompt>"
        """
        injected_prompt = self.format_injected_prompt(skill_content, user_prompt, cwd)
        return ["codex", "exec", injected_prompt]
