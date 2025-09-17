IMAGE ?= agentic-author:latest

build:
\tdocker build -t $(IMAGE) .

shell:
\tdocker run --rm -it --env OPENAI_API_KEY --volume $(PWD)/agentic_author_ai/data:/app/agentic_author_ai/data $(IMAGE) bash

demo:
\tdocker compose run --rm agentic-author

# Build FAISS index (expects chunks.json in data/)
index:
\tdocker compose run --rm agentic-author python -m agentic_author_ai.index

# Ask a question against the index
query:
\tdocker compose run --rm agentic-author python -m agentic_author_ai.query --q "$(Q)" $(ARGS)

# Optional: re-chunk raw PDFs/DOCX inside data/raw to chunks.json
chunk:
\tdocker compose run --rm agentic-author python -m agentic_author_ai.chunking --in agentic_author_ai/data/raw/*.pdf agentic_author_ai/data/raw/*.docx --out agentic_author_ai/data/chunks.json --jsonl
