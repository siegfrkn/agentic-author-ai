# agentic-author-ai
A python POC for an agentic AI system that is organized to write academic papers.

A tiny, composable agent framework written in Python.  
Includes:
- `Agent`, `Router`, `Memory`, and `Tool` primitives
- Example tools: `calc_tool`, `retrieve_tool`
- A demo pipeline with `Researcher` and `Writer` agents
- Support for either a dummy LLM (offline stub) or the OpenAI API

---

## Requirements

- **Python**: ≥ 3.12 (tested)
- **pip**: ≥ 24.0
- **virtualenv module**: `python3-venv` package installed on Ubuntu

### Python packages (minimum versions)

| Package        | Minimum | Notes                                        |
|----------------|---------|----------------------------------------------|
| `openai`       | 1.12.0  | For `client.chat.completions`. ≥1.40 adds `responses.create` |
| `typing-extensions` | 4.10.0 | Installed automatically with Python ≥3.12 |
| `setuptools`   | 68.0    | Ensure up-to-date inside venv                |
| `wheel`        | 0.42    | Recommended for builds                       |

*(Other dependencies are stdlib only.)*

---

## Setup

### 1. Clone / open project

Ensure you’re in the folder containing the `agentic_author_ai/` package.

### 2. Create a virtual environment

It’s safest to put your venv in Linux home if running under WSL:

```bash
# Install venv tools if missing
sudo apt update
sudo apt install -y python3-venv

# Create venv
python3 -m venv ~/venvs/agentic_author --upgrade-deps

# Activate it
source ~/venvs/agentic_author/bin/activate
```

*(If you prefer, you can also create `.venv` inside your project folder, but avoid `/mnt/c` if you see hangs in WSL2.)*

### 3. Upgrade core tools

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 4. Install dependencies

```bash
pip install --upgrade openai
```

---

## API Key Setup

The framework needs an OpenAI API key.

### Option A: Temporary export (per terminal session)

```bash
export OPENAI_API_KEY="sk-xxxx"
```

On Windows PowerShell:
```powershell
setx OPENAI_API_KEY "sk-xxxx"
```

### Option B: Permanent setup in `~/.bashrc`

Append this line to your `~/.bashrc` (Linux/WSL):

```bash
export OPENAI_API_KEY="sk-xxxx"
```

Reload:
```bash
source ~/.bashrc
```

## Running the Demo

From the project’s parent folder (with venv active):

```bash
python -m agentic_author_ai.demo
```

This will:
1. Seed system + user messages
2. Have the **Researcher** issue tool calls
3. Resolve tool calls via `Router`
4. Pass transcript to the **Writer** to summarize
5. Print the transcript and trace

---

## Switching LLMs

By default, `demo.py` uses `OpenAILLM`.

For offline testing (no API calls / quota issues), switch to `DummyLLM` in `demo.py`:

```python
from .llm import DummyLLM
researcher = Researcher(llm=DummyLLM())
writer = Writer(llm=DummyLLM())
```

---

## Known Issues

- **Quota exceeded (`429 insufficient_quota`)**: Means your OpenAI account has no free credits left; add billing details to continue.
- **Externally-managed pip**: On Ubuntu ≥22.04, use a venv to avoid `externally-managed-environment` errors.
- **Slow venv creation on `/mnt/c`**: Create the venv in `~/venvs/` instead and select it in VS Code when using WSL2 in Windows.

---

## Next Steps

- Upgrade `openai` to ≥1.40 for the unified `responses.create` API.
- Add config flag to toggle between `DummyLLM` and `OpenAILLM` without editing code.
- Extend with more real tools (retrieval, web calls, file I/O).
- Train models to specific research data.
