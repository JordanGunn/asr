"""GitHub Copilot agent driver."""

from pathlib import Path

from agents.base import AgentDriver


class CopilotDriver(AgentDriver):
    """Driver for GitHub Copilot CLI agent."""

    def get_name(self) -> str:
        """Get the agent name."""
        return "copilot"

    def get_binary_name(self) -> str:
        """Get the CLI binary name."""
        return "copilot"

    def build_command(
        self,
        skill_content: str,
        user_prompt: str,
        cwd: Path,
        extra_args: list[str] | None = None,
    ) -> list[str]:
        """Build copilot command.

        Copilot syntax: copilot -p "<prompt>"
        """
        injected_prompt = self.format_injected_prompt(skill_content, user_prompt, cwd)
        cmd = ["copilot"]
        if extra_args:
            cmd.extend(extra_args)
        cmd.extend(["-p", injected_prompt])
        return cmd
