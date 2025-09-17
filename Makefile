IMAGE ?= agentic-author:latest

build:
	docker build -t $(IMAGE) .

shell:
	docker run --rm -it \
		--env OPENAI_API_KEY \
		--volume $(PWD)/agentic_author_ai/data:/app/agentic_author_ai/data \
		$(IMAGE) bash

demo:
	docker compose run --rm agentic-author

# Build FAISS index (expects chunks.json in data/)
index:
	docker compose run --rm agentic-author python -m agentic_author_ai.index

# Ask a question against the index
query:
	docker compose run --rm agentic-author python -m agentic_author_ai.query --q "$(Q)" $(ARGS)

# Optional: re-chunk raw PDFs/DOCX inside data/raw to chunks.json
chunk:
	docker compose run --rm agentic-author python -m agentic_autho_
