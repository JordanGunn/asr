"""Agent driver registry and factory."""

from agents.base import AgentDriver
from agents.claude import ClaudeDriver
from agents.codex import CodexDriver
from agents.copilot import CopilotDriver
from agents.opencode import OpenCodeDriver

# Registry of all available drivers
DRIVERS: dict[str, type[AgentDriver]] = {
    "codex": CodexDriver,
    "copilot": CopilotDriver,
    "claude": ClaudeDriver,
    "opencode": OpenCodeDriver,
}


def get_driver(agent_name: str) -> AgentDriver:
    """Get driver instance by agent name.

    Args:
        agent_name: Name of agent (codex, copilot, claude).

    Returns:
        AgentDriver instance.

    Raises:
        ValueError: If agent name is invalid.
    """
    if agent_name not in DRIVERS:
        valid = ", ".join(sorted(DRIVERS.keys()))
        raise ValueError(f"Invalid agent '{agent_name}'. Must be one of: {valid}")

    return DRIVERS[agent_name]()


def detect_available_agents() -> list[str]:
    """Detect which agent binaries are available in PATH.

    Returns:
        List of available agent names.
    """
    available = []
    for name, driver_class in DRIVERS.items():
        driver = driver_class()
        if driver.detect():
            available.append(name)
    return sorted(available)


def get_all_agent_names() -> list[str]:
    """Get all supported agent names.

    Returns:
        List of all agent names.
    """
    return sorted(DRIVERS.keys())
