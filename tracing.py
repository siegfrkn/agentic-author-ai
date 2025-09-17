# -------------------------------
# Tracing
# -------------------------------

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
import contextlib
import time

@dataclass
class TraceEvent:
    ts: float
    name: str
    meta: Dict[str, float]

TRACE_LOG: List[TraceEvent] = []

@contextlib.contextmanager
def trace_span(name: str, **meta):
    start = time.time()
    try:
        yield
    finally:
        dur = time.time() - start
        TRACE_LOG.append(TraceEvent(time.time(), name, {**meta, "duration_s": round(dur, 4)}))

def dump_trace() -> str:
    rows = [f"- {e.name} ({e.meta.get('duration_s','?')}s)" for e in TRACE_LOG]
    return "Trace:\n" + "\n".join(rows)