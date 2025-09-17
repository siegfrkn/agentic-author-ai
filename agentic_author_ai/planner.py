# planner.py
"""Planner: alias for the existing Router to keep backwards compatibility.
If your code imports Router elsewhere, you can gradually switch to Planner.
"""
try:
    from .router import Router as Planner  # package import
except Exception:  # script mode fallback
    from router import Router as Planner  # type: ignore
