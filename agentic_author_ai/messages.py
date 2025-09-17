# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Katrina Nicole Siegfried
# Author: Katrina Nicole Siegfried
# Note: Portions of this file were drafted/edited with AI assistance and reviewed by the author.

# -------------------------------
# Messages
# -------------------------------

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict

Role = str # "user" | "assistant" | "system" | "tool" | agent name

@dataclass
class Message:
    role: Role
    content: str
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"role": self.role, "content": self.content, "meta": self.meta}