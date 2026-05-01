# Knowbot AI

Retrieval-augmented QA bot for AI/ML topics. Streamlit UI, Qdrant vector search, and LLM/embedding calls routed through the CoreNest API layer (FastAPI gateway unifying multiple LLM providers behind one authenticated API).

Live app: https://knowbot-ai.streamlit.app/

- Fast semantic search over pre-seeded Wikipedia AI/ML articles
- Gemini embeddings + completions via CoreNest
- Qdrant vector store with Wikipedia metadata payloads
- Streamlit UI with “continue on ChatGPT” handoff

## Architecture
- **UI**: Streamlit (`app/ui/streamlit_app.py`) handles input and response rendering.
- **Runtime RAG**: (`lib/pipeline/rag.py`) orchestrates query embedding, retrieval, context assembly, and completion generation.
- **Integrations**: (`lib/clients/`) wraps CoreNest and Qdrant access.
- **Pipeline Data**: (`lib/pipeline/prompts/`, `lib/pipeline/topics.yaml`) stores prompt templates and the ingestion topic list.
- **Ingestion**: (`lib/pipeline/ingestion.py`) splits text, filters low-value chunks, embeds with Gemini, and upserts to Qdrant.
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
Logs are emitted to stdout (see `app/config/logging.py`).

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
- `app/ui/streamlit_app.py` — Streamlit UI
- `app/config/*` — constants and logging
- `lib/pipeline/rag.py` — runtime RAG orchestration
- `lib/pipeline/prompts/*` — prompt templates used to build completion request params
- `lib/pipeline/topics.yaml` — flat topic list used for Wikipedia ingestion
- `lib/clients/*` — CoreNest and Qdrant integrations
- `lib/pipeline/ingestion.py` — Wikipedia ingestion pipeline
- `lib/utils/*` — shared utility helpers
- `tasks.py` — Invoke task collection

## Notes
- RAG flow falls back to “no info” if Qdrant returns no context or payloads are empty.
- The ChatGPT handoff button encodes the original query and model response for deeper exploration.
