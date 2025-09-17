# Agentic Author AI

Agentic Author AI is a modular writing system that demonstrates how planning, retrieval, external research, authorship, and editing agents can work together. It is packaged in a Docker container so that it can run reproducibly without installing local dependencies.

---

## About

The system accepts a prompt, determines whether external sources are allowed, retrieves relevant internal notes (via RAG), optionally gathers reliable external web sources, and then composes a draft that is polished by an editing step. This setup is intended as a teaching and experimentation environment for multi-agent writing pipelines.

---

## Quickstart

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) (with Compose v2)
- `make` (standard on Linux/macOS; install `make` on Windows via WSL or package manager)
- An OpenAI API key

### Clone and build
```bash
git clone https://github.com/siegfrkn/agentic-author-ai.git
cd agentic-author-ai
make build
```

### Set API key
```bash
export OPENAI_API_KEY=sk-...
```

### Run the demo
```bash
make demo PROMPT="Write a 2-page paper on agentic AI for finance" SESSION="Lseg Notes"
```

This runs the full pipeline (Planner → RAG Retriever → optional Researcher → Author → Editor) inside the container.

---

## Makefile Targets

The `Makefile` provides shortcuts for common commands:

- **`make build`**  
  Builds the Docker image. Required after changing dependencies in `Dockerfile`.  
  Example: `make build`

- **`make demo PROMPT="..." [SESSION="..."] [extra args]`**  
  Runs the full demo.  
  Arguments:  
  - `PROMPT`: Required writing prompt.  
  - `SESSION`: Optional session label to filter RAG notes.  
  - Extra args (optional):
    - `--force-external` or `--no-external` to override planner’s decision.
    - `--tone`, `--length`, `--format` to guide the Editor.
    - `--out FILE` to save the final draft.  
  Example:  
  ```bash
  make demo PROMPT="Draft a LinkedIn post about AI in healthcare" SESSION="Natwest" --tone="executive concise"
  ```

- **`make index`**  
  Builds a FAISS index from pre-chunked documents. Expects `chunks.json` or `chunks.jsonl` in `agentic_author_ai/data/`.

- **`make query Q="..." [ARGS='--filter ...']`**  
  Queries the FAISS index directly.  
  Example:  
  ```bash
  make query Q="What are the key takeaways from the LSEG session?" ARGS='--filter session "Lseg Notes"'
  ```

- **`make chunk`**  
  Splits raw PDF/DOCX files in `agentic_author_ai/data/raw/` into `chunks.json` for indexing.  
  Example:  
  ```bash
  make chunk
  make index
  ```

---

## Example End-to-End Usage

1. Place session notes (`.pdf` or `.docx`) into `agentic_author_ai/data/raw/`.  
2. Chunk into JSON:  
   ```bash
   make chunk
   ```
3. Build FAISS index:  
   ```bash
   make index
   ```
4. Ask a question:  
   ```bash
   make query Q="Summarize NatWest AI themes" ARGS='--filter session "Natwest"'
   ```
5. Run a full authored piece:  
   ```bash
   make demo PROMPT="Write a 2-page paper on AI regulation trends" SESSION="Natwest" --tone="formal" --out data/regulation.md
   ```

---
