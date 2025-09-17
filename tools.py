from __future__ import annotations
import inspect
import re
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict

# -------------------------------
# Core Tool types
# -------------------------------
ToolFn = Callable[..., Awaitable[str]]

@dataclass
class Tool:
    name: str
    description: str
    parameters: Dict[str, Any]
    func: ToolFn

    async def __call__(self, **kwargs) -> str:
        # simple schema guard
        for k in kwargs:
            if k not in self.parameters:
                raise TypeError(f"Unexpected parameter '{k}' for tool '{self.name}'")
        return await self.func(**kwargs)

def tool(name: str | None = None, description: str = "", parameters: Dict[str, Any] | None = None):
    """Decorator to wrap an async function into a Tool instance (not used below, but handy)."""
    def decorator(fn: ToolFn):
        t = Tool(
            name=name or fn.__name__,
            description=description or (inspect.getdoc(fn) or ""),
            parameters=parameters or {},
            func=fn,
        )
        t._is_tool = True  # type: ignore[attr-defined]
        return t
    return decorator

# -------------------------------
# Example tools used by demo.py
# -------------------------------
async def _calc(expr: str) -> str:
    """A tiny, safe-ish calculator supporting + - * / and parentheses."""
    if not re.fullmatch(r"[0-9+\-*/().\s]+", expr):
        return "Calculator error: invalid characters"
    try:
        return str(eval(expr, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Calculator error: {e}"

calc_tool = Tool(
    name="calc",
    description="Evaluate a simple arithmetic expression.",
    parameters={"expr": "str: arithmetic expression"},
    func=_calc,
)

async def _retrieve(query: str) -> str:
    """Stub retrieval that echoes a query (replace with real RAG)."""
    return f"[retrieve] Top results for: {query}"

retrieve_tool = Tool(
    name="retrieve",
    description="Retrieve context related to a query (demo stub).",
    parameters={"query": "str: search query"},
    func=_retrieve,
)

# Optional export list (not required, but nice)
__all__ = [
    "Tool",
    "tool",
    "calc_tool",
    "retrieve_tool",
]
