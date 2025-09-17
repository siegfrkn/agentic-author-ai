# -------------------------------
# Agent
# -------------------------------

from __future__ import annotations
from typing import Dict, Optional, Sequence
from .messages import Message
from .memory import Memory
from .llm import LLM, DummyLLM
from .tools import Tool

class Agent:
    def __init__(self, name: str, system_prompt: str, llm: Optional[LLM] = None, tools: Optional[Sequence[Tool]] = None, memory: Optional[Memory] = None):
        self.name = name
        self.system_prompt = system_prompt
        self.llm = llm or DummyLLM()
        self.tools: Dict[str, Tool] = {t.name: t for t in (tools or [])}
        self.memory = memory or Memory()

    def add_tool(self, t: Tool) -> None:
        self.tools[t.name] = t

    def prompt_from(self, messages: Sequence[Message]) -> str:
        header = f"System({self.name}): {self.system_prompt}\n"
        body = "\n".join(f"{m.role}: {m.content}" for m in messages)
        toollist = "\nTools: " + ", ".join(self.tools) if self.tools else ""
        return header + body + toollist + "\nAssistant:"

    async def act(self, messages: Sequence[Message]) -> Message:
        prompt = self.prompt_from(messages)
        out = await self.llm.acomplete(prompt)
        msg = Message(role=self.name, content=out)
        self.memory.add(msg)
        return msg