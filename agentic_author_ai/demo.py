# demo_writer.py
"""
Demo: Prompt → Planner → Author (writes) → Editor (edits), all using RAG.

Usage:
    export OPENAI_API_KEY=sk-...
    python -m agentic_author_ai.demo --prompt "Write a 2-page paper on agentic AI for finance" --session "Lseg Notes"

Notes:
- The Author and Editor both call into the RAG pipeline via query.answer().
- The Planner coordinates outline → drafting → editing.
"""

import argparse, textwrap, os
from typing import List, Optional, Dict
from pathlib import Path

from .planner import Planner
from .query import answer
from .rag_config import CHAT_MODEL
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def llm_edit(text: str, prompt: str) -> str:
    """Editor pass: grammar, clarity, adherence to prompt; preserve citations if present."""
    sys = ("You are an expert editor. Improve grammar, clarity, and cohesion while preserving factual content "
           "and any bracketed citations like [source:pp.x-y] or [session:section]. "
           "Ensure the result directly addresses the original writing prompt.")
    user = f"Original prompt:\n{prompt}\n\nDraft to edit:\n{text}"
    r = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role":"system","content":sys},{"role":"user","content":user}],
        temperature=0.2,
    )
    return r.choices[0].message.content

class SimplePlanner:
    """A lightweight planner that creates an outline and orchestrates Author→Editor passes."""
    def __init__(self, prompt: str, session: Optional[str] = None):
        self.prompt = prompt
        self.session = session

    

    def make_outline(self) -> List[str]:
        q = (
            "Create a concise outline (4-7 sections with short titles) for the following writing prompt. "
            "Only output a bullet list with one section title per line.\n\n"
            f"Prompt: {self.prompt}"
        )
        outline_text = answer(q, filters={"session":[self.session]} if self.session else None, use_rerank=True)
        lines = [l.strip("-• ").strip() for l in outline_text.splitlines() if l.strip()]
        # keep only 4-7 items, fall back if needed
        out = [l for l in lines if len(l) < 140]
        return out[:7] or ["Introduction","Background","Approach","Applications","Risks & Mitigations","Conclusion"]

    def author_section(self, title: str) -> str:
        q = (
            "Write a focused section for a paper. "
            "Follow the title exactly; be specific, use the provided context only, and include citations like [source:pp.x-y] or [session:section]. "
            "Avoid generic filler. Keep it 2–4 paragraphs.\n\n"
            f"Section title: {title}\n"
            f"Overall prompt: {self.prompt}"
        )
        return answer(q, filters={"session":[self.session]} if self.session else None, use_rerank=True)

    def run(self) -> str:
        outline = self.make_outline()
        sections = []
        for title in outline:
            draft = self.author_section(title)
            edited = llm_edit(draft, self.prompt)
            sections.append(f"## {title}\n\n{edited.strip()}")
        paper = "# " + self.prompt.strip().rstrip(".") + "\n\n" + "\n\n".join(sections)
        return paper

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True, help="Writing prompt for the paper")
    ap.add_argument("--session", help="Optional RAG session filter (e.g., 'Lseg Notes')")
    args = ap.parse_args()

    # Planner orchestrates
    _ = Planner  # not used directly here, but kept to align with requested renaming

    planner = SimplePlanner(prompt=args.prompt, session=args.session)
    paper = planner.run()

    # Save to file and print a short preview
    out = Path("paper.md")
    out.write_text(paper, encoding="utf-8")
    print("Wrote", out.resolve())
    print("\n--- Preview ---\n")
    print("\n".join(paper.splitlines()[:40]))

if __name__ == "__main__":
    main()
