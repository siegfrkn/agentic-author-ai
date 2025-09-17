IMAGE ?= agentic-author:latest

build:
	docker build -t $(IMAGE) .

shell:
	docker run --rm -it \
		--env OPENAI_API_KEY \
		--volume $(PWD)/agentic_author_ai/data:/app/agentic_author_ai/data \
		$(IMAGE) bash

# Build FAISS index (expects chunks.json in data/)
index:
	docker compose run --rm agentic-author python -m agentic_author_ai.index

# Ask a question against the index
query:
	@if [ -z "$(Q)" ]; then \
		echo "Usage: make query Q=\"<your question>\" [ARGS='--filter session \"LSEG\"']"; \
		exit 1; \
	fi
	docker compose run --rm agentic-author \
		python -m agentic_author_ai.query --q "$(Q)" $(ARGS)

# Optional: re-chunk raw PDFs/DOCX inside data/raw to chunks.json
chunk:
	docker compose run --rm agentic-author \
		python -m agentic_author_ai.chunking \
		--in agentic_author_ai/data/raw/*.pdf agentic_author_ai/data/raw/*.docx \
		--out agentic_author_ai/data/chunks.json --jsonl
