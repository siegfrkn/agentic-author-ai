# agentic_author_ai/demo.py
from __future__ import annotations
import argparse
import json
import os
import sys
from typing import List, Optional, Dict, Any

from openai import OpenAI

# Internal RAG (your existing module)
from . import query as rag_query
# External research helper (from researcher.py you added)
from .researcher import gather_sources, SourceItem
# Light-touch editor (from editor.py you added)
from .editor import edit_text

# ------------- Setup -------------
def _require_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("Error: OPENAI_API_KEY is not set.", file=sys.stderr)
        sys.exit(2)
    return key

client = OpenAI(api_key=_require_api_key())


# ------------- Planner -------------
def _plan_with_policy(prompt: str) -> Dict[str, Any]:
    """
    Ask the Planner to decide whether external sources are allowed and return steps.
    Output MUST be JSON (no prose).
    """
    system = (
        "You are a planning agent for a writing system. You are doing your best to create a professional and"
        "academic response using the agent team for a given prompt. It is important to take any length limitations"
        "given in the prompt under strict consideration, but being concise is paramount, and if no length target is"
        "given, make the response as concise as possible and as short as possible to answer the prompt.\n"
        "Return STRICT JSON with keys:\n"
        "{\n"
        '  "allow_external": true|false,\n'
        '  "rationale": "1-2 sentences why",\n'
        '  "research_focus": ["topics to look up", ...],\n'
        '  "steps": ["concise step 1", "concise step 2", ...]\n'
        "}\n"
        "Rules:\n"
        "- If prompt requests or implies outside facts (e.g., 'own research', 'sources', 'cite', "
        "  policy/market/industry assessments), set allow_external=true.\n"
        "- If prompt forbids external sources or clearly indicates internal-notes-only, set false.\n"
        "- Output valid JSON only (double quotes, no Markdown, no commentary)."
    )

    r = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"PROMPT:\n{prompt}\n\nReturn JSON ONLY."},
        ],
    )
    raw = (r.choices[0].message.content or "").strip()
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("Planner output not an object")
        for required in ("allow_external", "steps"):
            if required not in data:
                raise ValueError(f"Missing key: {required}")
        data["allow_external"] = bool(data["allow_external"])
        if "rationale" not in data:
            data["rationale"] = ""
        if "research_focus" not in data or not isinstance(data["research_focus"], list):
            data["research_focus"] = []
        return data
    except Exception:
        # Conservative fallback: avoid web calls; still provide usable steps.
        return {
            "allow_external": False,
            "rationale": "Fallback (could not parse planner JSON).",
            "research_focus": [],
            "steps": ["Outline key sections", "Draft arguments", "Incorporate internal notes", "Revise", "Proofread"]
        }


# ------------- Internal RAG -------------
def _rag_retrieve(prompt: str, session: Optional[str] = None, k: int = 6) -> List[Dict[str, Any]]:
    """
    Calls your existing FAISS retriever.
    Returns a list of chunks, each a dict with at least 'content' (adjust if your schema differs).
    """
    filters = {}
    if session:
        filters["session"] = session
    try:
        chunks = rag_query.retrieve(prompt, k=k, include=filters)
        return chunks or []
    except Exception as e:
        print(f"RAG retrieval failed: {e}", file=sys.stderr)
        return []


# ------------- Author -------------
def _author(
    prompt: str,
    plan: Dict[str, Any],
    session: Optional[str],
    rag_chunks: Optional[List[Dict[str, Any]]],
    web_sources: Optional[List[SourceItem]],
) -> str:
    """
    Compose final draft using INTERNAL NOTES (RAG) and optional EXTERNAL SOURCES (web).
    """
    system = (
        "You are an excellent academic writer. Use INTERNAL NOTES faithfully (primary source). "
        "If EXTERNAL SOURCES are provided, integrate carefully, use short inline citations like [Site] or [Org, Year], "
        "and add a final 'Sources' section listing title and URL. Do not invent citations or facts."
    )

    # Plan text
    plan_text = "\n".join(f"- {s}" for s in plan.get("steps", []))

    # Internal notes
    rag_text = ""
    if rag_chunks:
        parts = []
        for c in rag_chunks[:12]:
            # Adjust field names if your chunk schema differs
            content = c.get("content") or c.get("text") or ""
            if content:
                parts.append(content.strip())
        if parts:
            rag_text = "\n\nINTERNAL NOTES (RAG):\n" + "\n\n".join(parts)

    # External sources
    src_text = ""
    if web_sources:
        lines = []
        for i, s in enumerate(web_sources, 1):
            lines.append(f"[{i}] {s.title}\n{s.url}\nExcerpt: {s.excerpt[:300]}...")
        src_text = "\n\nEXTERNAL SOURCES (web):\n" + "\n\n".join(lines)

    user = (
        f"SESSION: {session or 'N/A'}\n"
        f"PLANNER: allow_external={plan.get('allow_external')} | reason: {plan.get('rationale','')}\n"
        f"RESEARCH FOCUS: {', '.join(plan.get('research_focus', [])) or 'N/A'}\n\n"
        f"PLAN:\n{plan_text}\n\n"
        f"PROMPT:\n{prompt}\n"
        f"{rag_text}"
        f"{src_text}"
    )

    r = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.5,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return (r.choices[0].message.content or "").strip()


# ------------- CLI -------------
def main():
    parser = argparse.ArgumentParser(
        description="Agentic Author Demo (Planner controls external research; RAG always on; Editor finalizes)"
    )
    parser.add_argument("--prompt", "--q", dest="prompt", default=None, help="Writing prompt")
    parser.add_argument("--session", dest="session", default=None, help="Optional session/context hint for internal RAG")
    # Optional manual overrides (useful for testing)
    parser.add_argument("--force-external", action="store_true", help="Force external research on")
    parser.add_argument("--no-external", action="store_true", help="Force external research off")
    parser.add_argument("--max-sources", type=int, default=4, help="Max external sources to gather if enabled")
    # Editor preferences + file output
    parser.add_argument("--tone", default=None, help="Editor tone (e.g., 'formal', 'executive concise')")
    parser.add_argument("--length", default=None, help="Length hint (e.g., '600-800 words', '2 pages')")
    parser.add_argument("--format", dest="fmt", default=None, help="Format hint (e.g., 'markdown', 'memo')")
    parser.add_argument("--out", default=None, help="Write final output to this file (e.g., data/out.md)")

    args = parser.parse_args()

    prompt = args.prompt or "Write a short example to prove the pipeline works."
    session = args.session

    # 1) Planner decides policy + steps
    plan = _plan_with_policy(prompt)

    # 2) Apply CLI overrides (if any)
    if args.force_external:
        plan["allow_external"] = True
    if args.no_external:
        plan["allow_external"] = False

    # 3) Always retrieve INTERNAL notes (RAG)
    rag_chunks = _rag_retrieve(prompt, session=session, k=6)

    # 4) Conditionally do EXTERNAL research
    web_sources: Optional[List[SourceItem]] = None
    if plan.get("allow_external", False):
        # You can build a tighter web query; using prompt is okay as a baseline.
        q = (prompt[:160] + "...") if len(prompt) > 160 else prompt
        try:
            web_sources = gather_sources(q, max_sources=max(1, args.max_sources))
        except Exception as e:
            print(f"External research failed: {e}", file=sys.stderr)
            web_sources = None

    # 5) Author composes with both
    draft = _author(prompt, plan, session=session, rag_chunks=rag_chunks, web_sources=web_sources)

    # 6) Editor finalizes
    final_text = edit_text(draft, tone=args.tone, length_hint=args.length, format_hint=args.fmt)

    # 7) Console summary + optional save
    print("\n=== PLAN (from Planner) ===")
    print(json.dumps(plan, indent=2))

    if rag_chunks:
        print(f"\n=== INTERNAL NOTES fetched (RAG): {len(rag_chunks)} chunks ===")

    if web_sources:
        print("\n=== EXTERNAL SOURCES (auto-collected) ===")
        for i, s in enumerate(web_sources, 1):
            print(f"[{i}] {s.title}\n{s.url}\nExcerpt: {s.excerpt[:200]}...\n")

    print("\n=== DRAFT (edited) ===\n" + final_text)

    if args.out:
        # Create directory if needed (handles plain filenames too)
        outdir = os.path.dirname(args.out)
        if outdir:
            os.makedirs(outdir, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(final_text)
        print(f"\n[saved to {args.out}]")


if __name__ == "__main__":
    main()
