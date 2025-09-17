# agentic_author_ai/editor.py
from __future__ import annotations
import os
from typing import Optional
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def edit_text(draft: str,
              tone: Optional[str] = None,
              length_hint: Optional[str] = None,
              format_hint: Optional[str] = None) -> str:
    """Light-touch revision: clarity, structure, consistency, citation sanity."""
    system = (
        "You are an expert editor. Improve clarity, flow, and structure. "
        "Preserve meaning. Keep citations, add missing section headers if helpful." 
        "Being concise is important, ensure the response is organized and concise, remove"
        "redundant information."
        "If citations look weak, keep them but flag with '(verify)'."
    )
    prefs = []
    if tone: prefs.append(f"Tone: {tone}.")
    if length_hint: prefs.append(f"Length: {length_hint}.")
    if format_hint: prefs.append(f"Format: {format_hint}.")
    prefs_txt = " ".join(prefs) or "Default tone and length."

    user = f"Editing preferences: {prefs_txt}\n\nDRAFT:\n{draft}"
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
    )
    return r.choices[0].message.content.strip()
