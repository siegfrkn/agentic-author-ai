# -------------------------------
# Router
# -------------------------------

from __future__ import annotations
import dataclasses
import json
import re
from typing import Dict, List, Sequence
from .agent import Agent
from .messages import Message
from .tracing import trace_span

class Router:
    TOOL_PATTERN = re.compile(r"\[\[tool:(?P<name>[a-zA-Z0-9_\-]+)\s+(?P<json>\{.*?\})\]\]")

    def __init__(self, agents: Dict[str, Agent]):
        self.agents = agents
        self.transcript: List[Message] = []

    def add(self, msg: Message) -> None:
        self.transcript.append(msg)
        for a in self.agents.values():
            a.memory.add(msg)

    async def run_turn(self, agent_name: str) -> Message:
        agent = self.agents[agent_name]
        reply = await agent.act(self.transcript)
        async for patched in self._resolve_tools(agent, reply):
            reply = patched
        self.add(reply)
        return reply

    async def _resolve_tools(self, agent: Agent, reply: Message):
        content = reply.content
        while True:
            m = self.TOOL_PATTERN.search(content)
            if not m:
                break
            tool_name = m.group("name")
            args = json.loads(m.group("json"))
            if tool_name not in agent.tools:
                obs = f"[tool:{tool_name}] not found"
            else:
                with trace_span(f"tool:{tool_name}"):
                    obs = await agent.tools[tool_name](**args)
            content = content[: m.start()] + obs + content[m.end():]
            reply = dataclasses.replace(reply, content=content)
            yield reply
        return

    async def chat(self, plan: Sequence[str], user_prompt: str):
        self.add(Message(role="user", content=user_prompt))
        out = []
        for name in plan:
            out.append(await self.run_turn(name))
        return out
