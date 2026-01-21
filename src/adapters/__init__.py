"""Adapter modules for generating IDE-specific skill files."""

from adapters.base import BaseAdapter
from adapters.cursor import CursorAdapter
from adapters.windsurf import WindsurfAdapter
from adapters.codex import CodexAdapter

__all__ = ["BaseAdapter", "CursorAdapter", "WindsurfAdapter", "CodexAdapter"]
