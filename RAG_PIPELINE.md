# Retrieval-Augmented Generation (RAG) Pipeline

This document explains how the input data was parsed into JSON, how RAG works, and why we chose this approach.

---

## Why RAG?

- **No training data**: notes are sparse, heterogeneous, and small.
- **Fast to update**: drop in new PDFs/DOCX → regenerate chunks → rebuild index.
- **Grounded answers**: models don’t hallucinate beyond the provided chunks.
- **Traceable**: every answer can cite `[session:pp.page-range]`.

---

## Step 1: Parsing & Chunking

Raw inputs: PDF/DOCX session notes (e.g., `ks-natwest-notes.docx`).

Wrote `chunking.py` to:

1. Extract text (via PyPDF2, pdfminer, or python-docx).
2. Clean formatting (strip whitespace, normalize).
3. Break into ~800-word **chunks** (with ~100 word overlap).
4. Add metadata:  
   - `source` (filename)  
   - `session` (human-readable)  
   - `speaker` (inferred from text)  
   - `page_start/page_end`  

Output: `chunks.json` (array) and `chunks.jsonl` (JSON lines).

Example chunk:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "text": "Holistic AI described their approach...",
  "meta": {
    "source": "ks-holistic-ai-notes.pdf",
    "session": "Holistic Ai Notes",
    "speaker": ["Mihir T", "Graham S"],
    "page_start": 2,
    "page_end": 3
  }
}
