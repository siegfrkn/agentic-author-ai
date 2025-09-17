# query.py
"""
Step 3 & 4: Retrieval, optional re-ranking, and grounded answering.
Provides make_retrieve_tool(ToolClass) to integrate with your framework.
"""

import argparse, json, re, numpy as np, faiss, os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .rag_config import (
    FAISS_INDEX, FAISS_METADATA, CHAT_MODEL, EMBED_MODEL,
    TOP_K, RERANK_TOPN, MAX_CTX_CHARS
)

from openai import OpenAI

def load_index_meta():
    index = faiss.read_index(str(FAISS_INDEX))
    meta  = json.loads(Path(FAISS_METADATA).read_text())
    return index, meta

def _client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_query(q: str) -> np.ndarray:
    client = _client()
    r = client.embeddings.create(model=EMBED_MODEL, input=[q])
    v = np.array(r.data[0].embedding, dtype="float32").reshape(1, -1)
    faiss.normalize_L2(v)
    return v

def retrieve(query: str, k: int = TOP_K,
             include: Optional[Dict[str, List[str]]] = None) -> List[Dict[str, Any]]:
    index, meta = load_index_meta()
    v = embed_query(query)
    D, I = index.search(v, k * 8)
    cands = [meta[i] for i in I[0] if i != -1]

    if include:
        def keep(c):
            m = c.get("meta", {})
            for key, vals in include.items():
                mv = m.get(key)
                if isinstance(mv, list):
                    if not any(v in mv for v in vals): return False
                else:
                    if mv not in vals: return False
            return True
        cands = [c for c in cands if keep(c)]

    out, seen = [], set()
    for c in cands:
        tag = (c["meta"].get("source",""), c["meta"].get("section",""))
        if tag in seen: continue
        seen.add(tag)
        out.append(c)
        if len(out) >= k: break
    return out

def rerank(query: str, chunks: List[Dict[str, Any]], topn: int = RERANK_TOPN) -> List[Dict[str, Any]]:
    client = _client()
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for c in chunks:
        prompt = (
            f"Query: {query}\n\n"
            f"Chunk:\n{c['text'][:2000]}\n\n"
            "Only output a number from 0-10 for usefulness."
        )
        r = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        txt = (r.choices[0].message.content or "").strip()
        try:
            num = float(re.findall(r"[0-9]+(?:\.[0-9]+)?", txt)[0])
        except Exception:
            num = 0.0
        scored.append((num, c))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [c for _, c in scored[:topn]]

SYSTEM = (
    "You are a careful assistant. Use ONLY the provided context. "
    "If the answer is not in the context, say you don't know. "
    "Cite sources as [source:pp.start-end] or [session:section]. Be concise."
)

def build_context(chunks: List[Dict[str, Any]], max_chars: int = MAX_CTX_CHARS) -> str:
    blocks = []
    for c in chunks:
        m = c.get("meta", {})
        label = m.get("source") or m.get("session") or "source"
        pstart, pend = m.get("page_start"), m.get("page_end")
        cite = f"{label}"
        if pstart and pend: cite += f":pp.{pstart}-{pend}"
        section = m.get("section")
        if section: cite += f" §{section}"
        blocks.append(f"[{cite}]\n{c['text']}")
    return "\n\n---\n\n".join(blocks)[:max_chars]

def answer(query: str,
           filters: Optional[Dict[str, List[str]]] = None,
           use_rerank: bool = True) -> str:
    chunks = retrieve(query, k=TOP_K, include=filters)
    if use_rerank and chunks:
        chunks = rerank(query, chunks, topn=min(RERANK_TOPN, len(chunks)))
    ctx = build_context(chunks)
    client = _client()
    r = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Question: {query}\n\nContext:\n{ctx}"}
        ],
        temperature=0.2,
    )
    return r.choices[0].message.content

# -----------------
# Tool factory (no circular import)
# -----------------
def make_retrieve_tool(ToolClass):
    """Factory that creates a Tool instance using the provided Tool class."""
    async def _retrieve(query: str, session: Optional[str] = None) -> str:
        filters = {"session": [session]} if session else None
        chunks = retrieve(query, k=TOP_K, include=filters)
        lines = [f"[retrieve] {len(chunks)} matches for: {query}"]
        for c in chunks[:5]:
            m = c.get("meta", {})
            src = m.get("source", "")
            sec = m.get("section", "")
            lines.append(f"- {src} §{sec}: {c['text'][:160].replace('\\n',' ')}…")
        return "\n".join(lines)
    return ToolClass(
        name="retrieve",
        description="Retrieve RAG context for a query (with optional session filter).",
        parameters={"query": "str", "session": "Optional[str]"},
        func=_retrieve,
    )

# CLI
def _cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", required=True, help="User query")
    ap.add_argument("--filter", nargs=2, metavar=("KEY","VALUE"),
                    action="append", help="Filter like: --filter session 'Lseg Notes'")
    ap.add_argument("--no-rerank", action="store_true", help="Disable LLM re-ranking")
    args = ap.parse_args()

    filters = None
    if args.filter:
        filters = {}
        for k, v in args.filter:
            filters.setdefault(k, []).append(v)

    print(answer(args.q, filters=filters, use_rerank=not args.no_rerank))

if __name__ == "__main__":
    _cli()
