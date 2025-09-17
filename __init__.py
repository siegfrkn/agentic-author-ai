"""aagentic-author-ai: a tiny, composable agent framework for writing (stdlib-only)"""

from .tools import Tool, tool, retrieve_tool
from .router import Router
from .planner import Planner

__all__ = [
    "Tool",
    "tool",
    "retrieve_tool",
    "Router",
    "Planner",
]
