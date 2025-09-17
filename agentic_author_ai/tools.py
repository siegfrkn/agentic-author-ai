# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Katrina Nicole Siegfried
# Author: Katrina Nicole Siegfried
# Note: Portions of this file were drafted/edited with AI assistance and reviewed by the author.

# -------------------------------
# Tools
# -------------------------------

"""
Your tool definitions. Now wires the real RAG retriever.
"""

from .query import make_retrieve_tool

# Your existing Tool class / decorator
class Tool:
    def __init__(self, name: str, description: str, parameters: dict, func):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func

    async def __call__(self, **kwargs):
        return await self.func(**kwargs)

def tool(*args, **kwargs):
    """Decorator for turning a function into a Tool"""
    def decorator(func):
        return Tool(*args, func=func, **kwargs)
    return decorator

# Build RAG-backed retriever here
retrieve_tool = make_retrieve_tool(Tool)

# You can keep defining other tools below as before...
# e.g.
# echo_tool = Tool(
#     name="echo",
#     description="Echo back text",
#     parameters={"text": "str"},
#     func=lambda text: text
# )
