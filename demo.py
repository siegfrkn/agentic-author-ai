# -------------------------------
# Demo
# -------------------------------

from __future__ import annotations
import asyncio
import random
from .agent import Agent
from .llm import OpenAILLM  # <-- use OpenAI adapter
from .messages import Message
from .router import Router
from .tools import calc_tool, retrieve_tool
from .tracing import dump_trace

class Researcher(Agent):
    def __init__(self):
        super().__init__(
            name="Researcher",
            system_prompt=(
                "You are a concise research assistant. Identify key facts, missing info,\n"
                "and call tools where helpful. Prefer bullet points."
            ),
            llm=OpenAILLM(model="gpt-4o-mini"),
            tools=[calc_tool, retrieve_tool],
        )

class Writer(Agent):
    def __init__(self):
        super().__init__(
            name="Writer",
            system_prompt=(
                "You transform research into a clear, user-friendly answer. Cite any\n"
                "tool outputs inline. Keep it under 8 bullets or 200 words."
            ),
            llm=OpenAILLM(model="gpt-4o-mini"),
            tools=[calc_tool],
        )

async def run_demo() -> None:
    random.seed(42)
    router = Router({"Researcher": Researcher(), "Writer": Writer()})

    user_prompt = (
        "Compare the monthly cost of two SaaS plans: Plan A is $19.99/user for 12 users;\n"
        "Plan B is $15/user for 12 users plus a $50 base fee. Show the math with a calculator,\n"
        "then summarize which is cheaper and by how much."
    )

    # Seed a calculation hint so the router resolves tool calls in this demo
    tool_hint = (
        "\n[[tool:calc {\"expr\":\"(19.99*12)\"}]]\n"
        "\n[[tool:calc {\"expr\":\"(15*12)+50\"}]]\n"
    )

    router.add(Message(role="system", content="Demo started"))
    router.add(Message(role="user", content=user_prompt))
    router.add(Message(role="Researcher", content=f"Calculations:{tool_hint}"))

    await router.run_turn("Writer")

    print("\n=== Transcript ===")
    for m in router.transcript:
        if m.role == "system":
            continue
        print(f"[{m.role}] {m.content}")

    print("\n" + dump_trace())

if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        pass
