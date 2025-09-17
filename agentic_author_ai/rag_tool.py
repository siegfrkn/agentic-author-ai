# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Katrina Nicole Siegfried
# Author: Katrina Nicole Siegfried
# Note: Portions of this file were drafted/edited with AI assistance and reviewed by the author.

# -------------------------------
# RAG Tool
# -------------------------------

"""
Drop-in Tool for your agent framework using the RAG index built by index.py.

Use in your code by replacing:
    from .tools import retrieve_tool
with:
    from .rag_tool import retrieve_tool

This will wire the demo and any agents to the real retriever.
"""

# Flexible import of Tool and query helpers (package or script modes)
try:
    from .tools import Tool  # your Tool class
    from .query import make_retrieve_tool  # factory
except Exception:
    from tools import Tool  # type: ignore
    from query import make_retrieve_tool  # type: ignore

# Build a Tool instance named "retrieve" that uses the RAG pipeline
retrieve_tool: Tool = make_retrieve_tool()
