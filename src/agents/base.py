"""Abstract base class for agent drivers."""

import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path


class AgentDriver(ABC):
    """Abstract base class for AI agent CLI drivers."""

    @abstractmethod
    def get_name(self) -> str:
        """Get the agent name.

        Returns:
            Agent name (e.g., 'codex', 'copilot', 'claude').
        """

    @abstractmethod
    def get_binary_name(self) -> str:
        """Get the CLI binary name to check for.

        Returns:
            Binary name (e.g., 'codex', 'copilot', 'claude').
        """

    def detect(self) -> bool:
        """Check if the agent binary is available in PATH.

        Returns:
            True if binary is found, False otherwise.
        """
        return shutil.which(self.get_binary_name()) is not None

    @abstractmethod
    def build_command(self, skill_content: str, user_prompt: str, cwd: Path) -> list[str]:
        """Build the command to execute.

        Args:
            skill_content: Full SKILL.md content.
            user_prompt: User's prompt/request.
            cwd: Current working directory.

        Returns:
            Command as list of strings (for subprocess).
        """

    def execute(self, skill_content: str, user_prompt: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
        """Execute skill with agent.

        Args:
            skill_content: Full SKILL.md content.
            user_prompt: User's prompt/request.
            cwd: Working directory for execution (defaults to current dir).

        Returns:
            CompletedProcess with stdout/stderr/returncode.

        Raises:
            FileNotFoundError: If agent binary not found.
        """
        if not self.detect():
            raise FileNotFoundError(f"{self.get_name()} binary '{self.get_binary_name()}' not found in PATH")

        working_dir = cwd or Path.cwd()
        cmd = self.build_command(skill_content, user_prompt, working_dir)

        return subprocess.run(
            cmd,
            cwd=working_dir,
            capture_output=False,  # Stream to stdout/stderr
            text=True,
        )

    def format_injected_prompt(self, skill_content: str, user_prompt: str, cwd: Path) -> str:
        """Format the injected prompt with skill content.

        Args:
            skill_content: Full SKILL.md content.
            user_prompt: User's prompt/request.
            cwd: Current working directory.

        Returns:
            Formatted prompt string.
        """
        return f"""You are executing a skill. Follow these instructions carefully:

━━━━━━━━ SKILL INSTRUCTIONS ━━━━━━━━
{skill_content}
━━━━━━━━ END SKILL ━━━━━━━━

USER REQUEST: {user_prompt}

Working directory: {cwd}
Execute the skill above for this request."""
