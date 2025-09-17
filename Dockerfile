# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Avoid Python writing .pyc files & turn off buffering
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System packages (build tools for some wheels, and common libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git tini \
    && rm -rf /var/lib/apt/lists/*

# Create app dir
WORKDIR /app

# Copy only dependency hints first for better layer caching
# (If you add a requirements.txt later, this will cache nicely)
COPY README.md ./

# Install Python deps (use wheels where possible)
# Minimal set based on your README; add optional parsers used by chunking.
RUN pip install --upgrade pip \
 && pip install \
    openai>=1.12.0 \
    faiss-cpu \
    numpy \
    pypdf \
    python-docx \
    duckduckgo-search \
    readability-lxml \
    requests \
    lxml

# Copy project
COPY . /app

# Create a writable data dir (mounted via volume in compose)
RUN mkdir -p /app/agentic_author_ai/data

# Non-root user (safer)
RUN useradd -m app && chown -R app:app /app
USER app

# Default environment placeholders
ENV OPENAI_API_KEY=""

# Use tini as a minimal init
ENTRYPOINT ["/usr/bin/tini", "--"]

# Default command prints help
CMD ["python", "-m", "agentic_author_ai.demo"]
