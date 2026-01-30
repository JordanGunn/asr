"""Adapter modules for generating IDE-specific skill files."""

from adapters.base import BaseAdapter
from adapters.claude import ClaudeAdapter
from adapters.codex import CodexAdapter
from adapters.copilot import CopilotAdapter
from adapters.cursor import CursorAdapter
from adapters.windsurf import WindsurfAdapter

__all__ = [
    "BaseAdapter",
    "CursorAdapter",
    "WindsurfAdapter",
    "CodexAdapter",
    "CopilotAdapter",
    "ClaudeAdapter",
]
