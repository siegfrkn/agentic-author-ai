# index.py
"""
Step 2: Embed chunks and build FAISS index.

Usage:
    export OPENAI_API_KEY=sk-...
    pip install openai faiss-cpu numpy
    python -m index
"""

import json, numpy as np, faiss
from pathlib import Path
from typing import List
from .rag_config import CHUNKS_JSON, FAISS_INDEX, FAISS_METADATA, EMBED_MODEL

# OpenAI client
from openai import OpenAI
import os

def load_chunks() -> List[dict]:
    return json.loads(Path(CHUNKS_JSON).read_text())

def embed_texts(texts: List[str]) -> np.ndarray:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    B = 128
    out = []
    for i in range(0, len(texts), B):
        batch = texts[i:i+B]
        r = client.embeddings.create(model=EMBED_MODEL, input=batch)
        out.extend([d.embedding for d in r.data])
    X = np.array(out, dtype="float32")
    faiss.normalize_L2(X)
    return X

def main():
    chunks = load_chunks()
    texts = [c["text"] for c in chunks]
    X = embed_texts(texts)

    index = faiss.IndexFlatIP(X.shape[1])
    index.add(X)

    faiss.write_index(index, str(FAISS_INDEX))
    Path(FAISS_METADATA).write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")

    print(f"Indexed {len(chunks)} chunks → {FAISS_INDEX.name}, meta → {FAISS_METADATA.name}")

if __name__ == "__main__":
    main()
