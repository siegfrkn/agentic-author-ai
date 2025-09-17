# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Katrina Nicole Siegfried
# Author: Katrina Nicole Siegfried
# Note: Portions of this file were drafted/edited with AI assistance and reviewed by the author.

# -------------------------------
# Memory
# -------------------------------

from __future__ import annotations
from pathlib import Path
from typing import List, Optional, Union
from .messages import Message
import json

class Memory:
    """Very small memory with scratchpad and optional JSONL persistence."""

    def __init__(self, persist_path: Optional[Union[str, Path]] = None, max_scratch: int = 50):
        self.scratch: List[Message] = []
        self.persist_path = Path(persist_path) if persist_path else None
        self.max_scratch = max_scratch
        if self.persist_path:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, msg: Message) -> None:
        self.scratch.append(msg)
        if len(self.scratch) > self.max_scratch:
            self.scratch.pop(0)
        if self.persist_path:
            with open(self.persist_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(msg.to_dict(), ensure_ascii=False) + "\n")

    def last(self, n: int = 1):
        return self.scratch[-n:]

    def all(self):
        return list(self.scratch)