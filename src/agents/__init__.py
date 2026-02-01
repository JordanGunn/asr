"""Agent driver system."""

from agents.base import AgentDriver
from agents.claude import ClaudeDriver
from agents.codex import CodexDriver
from agents.copilot import CopilotDriver
from agents.opencode import OpenCodeDriver
from agents.registry import (
    DRIVERS,
    detect_available_agents,
    get_all_agent_names,
    get_driver,
)

__all__ = [
    "AgentDriver",
    "CodexDriver",
    "CopilotDriver",
    "ClaudeDriver",
    "OpenCodeDriver",
    "DRIVERS",
    "get_driver",
    "detect_available_agents",
    "get_all_agent_names",
]
