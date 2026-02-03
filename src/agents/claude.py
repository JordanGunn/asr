"""Claude CLI agent driver."""

from pathlib import Path

from agents.base import AgentDriver


class ClaudeDriver(AgentDriver):
    """Driver for Claude CLI agent."""

    def get_name(self) -> str:
        """Get the agent name."""
        return "claude"

    def get_binary_name(self) -> str:
        """Get the CLI binary name."""
        return "claude"

    def build_command(
        self,
        skill_content: str,
        user_prompt: str,
        cwd: Path,
        extra_args: list[str] | None = None,
    ) -> list[str]:
        """Build claude command.

        Claude syntax: claude <prompt> -p
        """
        injected_prompt = self.format_injected_prompt(skill_content, user_prompt, cwd)
        cmd = ["claude"]
        if extra_args:
            cmd.extend(extra_args)
        cmd.extend([injected_prompt, "-p"])
        return cmd
