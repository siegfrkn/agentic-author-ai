# rag_config.py
"""
Central config for your RAG pipeline.
Edit paths/models here and all modules will stay in sync.
"""

from pathlib import Path

# Storage locations (default to repo-local "data/" folder if present, else /mnt/data)
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Artifacts
CHUNKS_JSON     = DATA_DIR / "chunks.json"
CHUNKS_JSONL    = DATA_DIR / "chunks.jsonl"
FAISS_INDEX     = DATA_DIR / "rag.faiss"
FAISS_METADATA  = DATA_DIR / "rag_meta.json"

# Models
EMBED_MODEL = "text-embedding-3-large"   # or "text-embedding-3-small" for speed/cost
CHAT_MODEL  = "gpt-4.1-mini"             # can swap to your preferred chat model

# Retrieval defaults
TOP_K          = 8
RERANK_TOPN    = 6
MAX_CTX_CHARS  = 12000
