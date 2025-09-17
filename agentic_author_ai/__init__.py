"""aagentic-author-ai: a tiny, composable agent framework for writing (stdlib-only)"""

from .tools import Tool, tool, retrieve_tool
from .planner import Planner

__all__ = [
    "Tool",
    "tool",
    "retrieve_tool",
    "Planner",
]
