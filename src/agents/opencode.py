"""OpenCode CLI agent driver."""

from pathlib import Path

from agents.base import AgentDriver


class OpenCodeDriver(AgentDriver):
    """Driver for OpenCode CLI agent."""

    def get_name(self) -> str:
        """Get the agent name."""
        return "opencode"

    def get_binary_name(self) -> str:
        """Get the CLI binary name."""
        return "opencode"

    def build_command(self, skill_content: str, user_prompt: str, cwd: Path) -> list[str]:
        """Build opencode run command.

        OpenCode syntax: opencode run "<prompt>"
        """
        injected_prompt = self.format_injected_prompt(skill_content, user_prompt, cwd)
        return ["opencode", "run", injected_prompt]
