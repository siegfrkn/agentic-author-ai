# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Katrina Nicole Siegfried
# Author: Katrina Nicole Siegfried
# Note: Portions of this file were drafted/edited with AI assistance and reviewed by the author.

# -------------------------------
# LLM Interface
# -------------------------------

from __future__ import annotations
import asyncio
import functools
import random
from typing import Any

class LLM:
    """Abstract LLM interface. Implement 'complete' or 'acomplete'."""
    def complete(self, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError

    async def acomplete(self, prompt: str, **kwargs: Any) -> str:
        # default to sync complete in a thread
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, functools.partial(self.complete, prompt, **kwargs))


class DummyLLM(LLM):
    """Deterministic, tiny stand-in for a real LLM for testing/demo."""
    def __init__(self, seed: int = 7):
        self.rng = random.Random(seed)

    def complete(self, prompt: str, **kwargs: Any) -> str:
        # naive extract of last user line
        lines = [l.strip() for l in prompt.splitlines() if l.strip()]
        last = lines[-1] if lines else ""
        bullets = [f"- Insight {i}: {last[:80]} (stub)" for i in range(1, 4)]
        return "\n".join(["Here are some thoughts:"] + bullets + ["\n(Replace DummyLLM with a real model)"])


# -------------------------------
# OpenAI adapter for SDK 1.12.x (chat.completions)
# -------------------------------
import os
from typing import Any

class OpenAILLM(LLM):
    """
    Minimal adapter for openai==1.12.x using chat.completions.
    Set OPENAI_API_KEY in your environment. Example:
        export OPENAI_API_KEY="sk-..."
    """
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: str | None = None, **defaults: Any):
        # You can switch to "gpt-4o-mini" later if your account supports it with chat.completions
        self.model = model
        self.defaults = defaults
        from openai import OpenAI  # new-style client exists in 1.12.x
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        if not (api_key or os.getenv("OPENAI_API_KEY")):
            raise RuntimeError("OPENAI_API_KEY not set")

    def complete(self, prompt: str, **kwargs: Any) -> str:
        params = {**self.defaults, **kwargs}
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **params,
            )
            return resp.choices[0].message.content
        except Exception as e:
            # Surface the real error for fast debugging (auth/model/quota/network)
            raise RuntimeError(f"OpenAI chat.completions failed: {e}") from e
