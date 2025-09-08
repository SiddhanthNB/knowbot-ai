# Todo List

This file outlines the remaining tasks for building the RAG system.

## Data Ingestion Script (`scripts/ingest_data.py`)

The `scripts/ingest_data.py` script is responsible for loading the data, processing it, and storing it in the Qdrant vector database.

### 1. Text Splitting

- [ ] **Implement text splitting in `process_article_content`:** Use LangChain's `RecursiveCharacterTextSplitter` to split the content of each Wikipedia article into smaller chunks.
- [ ] **Configure the splitter:**
    -   `chunk_size`: 1000 (as discussed)
    -   `chunk_overlap`: 200 (as discussed)

### 2. Embedding

- [ ] **Implement the embedding logic:** Create a function to generate embeddings for the text chunks using the Gemini endpoint.
- [ ] **Use a synchronous HTTP client:** Use the `requests` library to make synchronous calls to the Gemini API.
- [ ] **Batch the requests:** To improve efficiency, send multiple text chunks in a single request to the Gemini API.

### 3. Upserting to Qdrant

- [ ] **Implement the Qdrant upsert logic:**
    -   Create a new Qdrant collection with a configurable name.
    -   Upsert the embedded chunks into the new collection. Each point in Qdrant should contain the embedding vector and the original text chunk as payload.
- [ ] **Handle Qdrant client:** Use the existing `get_qdrant_client` from `config/qdrant.py`.

## Configuration

- [ ] **Add Gemini configuration to `.env`:** Add the following new variables to your `.env` file:
    -   `GEMINI_API_BASE_URL`
    -   `GEMINI_EMBEDDING_MODEL`
    -   `GEMINI_API_KEY`
- [ ] **Update `utils/constants.py`:** Load the new Gemini configuration variables from the environment.

## Runtime (RAG)

- [ ] **Ensure consistent embedding model:** This is a critical point. The same Gemini embedding model (`GEMINI_EMBEDDING_MODEL`) must be used for both the ingestion script and the runtime RAG query embedding. The runtime query embedding logic in `streamlit_ui/gui.py` (which currently uses `corenest`) will need to be updated to use the same Gemini embedding endpoint as the ingestion script.
