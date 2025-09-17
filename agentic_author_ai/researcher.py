# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Katrina Nicole Siegfried
# Author: Katrina Nicole Siegfried
# Note: Portions of this file were drafted/edited with AI assistance and reviewed by the author.

# -------------------------------
# Researcher
# -------------------------------

from __future__ import annotations
import re
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import requests
from duckduckgo_search import DDGS
from readability import Document
from lxml import html  # noqa: F401

USER_AGENT = "agentic-author-ai/1.0 (+https://github.com/siegfrkn/agentic-author-ai)"
DEFAULT_TIMEOUT = 12

# Prefer reputable domains first; tweak as you like.
PREFERRED_DOMAINS = [
    "reuters.com", "bloomberg.com", "ft.com", "economist.com", "wsj.com",
    "oecd.org", "imf.org", "worldbank.org", "bis.org",
    "sec.gov", "treasury.gov", "gov.uk",
    "nature.com", "science.org", "sciencedirect.com",
    "mckinsey.com", "bcg.com", "bain.com",
    "nytimes.com", "bbc.com", "apnews.com"
]

BLOCKLIST = [
    "pinterest.", "reddit.", "quora.", "/amp", "youtube.com/shorts",
]

@dataclass
class SourceItem:
    title: str
    url: str
    excerpt: str

def _good_url(u: str) -> bool:
    if not u.startswith("http"):
        return False
    return not any(b in u for b in BLOCKLIST)

def _domain_score(u: str) -> int:
    for i, d in enumerate(PREFERRED_DOMAINS):
        if d in u:
            return 1000 - i
    return 0

def search_web(query: str, max_results: int = 8) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results, safesearch="moderate"):
            if r and "href" in r and _good_url(r["href"]):
                r["_score"] = _domain_score(r["href"])
                results.append(r)
    results.sort(key=lambda x: x.get("_score", 0), reverse=True)
    return results

def _fetch_excerpt(url: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[str]:
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        resp.raise_for_status()
        doc = Document(resp.text)
        text = re.sub(r"\s+", " ", html.fromstring(doc.summary()).text_content()).strip()
        if not text:
            return None
        return (text[:800] + "...") if len(text) > 800 else text
    except Exception:
        return None

def gather_sources(query: str, max_sources: int = 4, sleep_sec: float = 0.6) -> List[SourceItem]:
    raw = search_web(query, max_results=max_sources * 2)
    items: List[SourceItem] = []
    for r in raw:
        if len(items) >= max_sources:
            break
        url = r.get("href") or r.get("url") or ""
        title = r.get("title") or r.get("body") or url
        excerpt = _fetch_excerpt(url) or (r.get("body") or "")
        if not excerpt:
            continue
        items.append(SourceItem(title=title, url=url, excerpt=excerpt))
        time.sleep(sleep_sec)
    return items
