# Knowbot AI

Retrieval-augmented QA bot for AI/ML topics. Streamlit UI, Qdrant vector search, and LLM/embedding calls routed through the CoreNest API layer (FastAPI gateway unifying multiple LLM providers behind one authenticated API).

Live app: https://knowbot-ai.streamlit.app/

- Fast semantic search over pre-seeded Wikipedia AI/ML articles
- Gemini embeddings + completions via CoreNest
- Qdrant vector store with Wikipedia metadata payloads
- Streamlit UI with “continue on ChatGPT” handoff

## Architecture
- **UI**: Streamlit (`utils/streamlit/gui.py`) handles input, RAG call, and response rendering.
- **Retrieval**: Qdrant (`utils/helpers/qdrant.py`) stores 3072-dim Gemini embeddings; searches with score thresholds.
- **Model Gateway**: CoreNest (`utils/helpers/corenest.py`) wraps embeddings and completions endpoints with bearer auth.
- **Ingestion**: Wikipedia topic crawler/ingestor (`utils/helpers/injector.py`) splits text, filters low-value chunks, embeds with Gemini, and upserts to Qdrant.
- **Tasks**: Invoke commands in `tasks.py` for one-time collection lifecycle and data seeding.

## Prerequisites
- Python 3.12+
- Access to CoreNest endpoints and keys
- Access to a Qdrant cluster
- Google API key for Gemini embeddings
- `uv` (recommended) or `pip` for dependency installation

## Environment
Copy `.env.sample` to `.env` and fill with your values (sample lists all required keys):
```
APP_ENV=local
CORENEST_API_URL=...
CORENEST_SECRET_KEY=...
QDRANT_URL=...
QDRANT_COLLECTION_NAME=...
QDRANT_ACCESS_KEY=...
GOOGLE_API_KEY=...
```

## Setup
```bash
# from repo root
uv venv .venv               # creates .venv using uv
source .venv/bin/activate
uv sync                     # installs deps from pyproject/uv.lock into .venv
```

## Running locally
```bash
streamlit run main.py
```
Logs are emitted to stdout (see `config/logger.py`).

## Data seeding (optional)
Requires Qdrant reachable and `.env` filled.
```bash
source .venv/bin/activate
inv one-time-tasks.create-qdrant-collection
inv one-time-tasks.populate-qdrant-collection
# cleanup: inv one-time-tasks.delete-qdrant-collection
```

## Project structure
- `main.py` — Streamlit entrypoint
- `utils/streamlit/gui.py` — UI + RAG flow
- `utils/helpers/*` — CoreNest client, Qdrant client, ingestion utilities
- `config/*` — logging and Qdrant client wiring
- `utils/prompts/*` — system/user prompt templates
- `tasks.py` — Invoke task collection

## Notes
- RAG flow falls back to “no info” if Qdrant returns no context or payloads are empty.
- The ChatGPT handoff button encodes the original query and model response for deeper exploration.
