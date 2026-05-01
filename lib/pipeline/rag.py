from pathlib import Path

from app.config import constants
from lib.clients.corenest import fetch_embeddings, fetch_llm_response
from lib.clients.qdrant import perform_semantic_search

NO_INFO_MESSAGE = "I'm sorry, but I could not find any relevant information in my knowledge base to answer your question."
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def _load_prompt_templates():
    system_prompt = (PROMPTS_DIR / "system_prompt.txt").read_text(encoding="utf-8")
    user_prompt = (PROMPTS_DIR / "user_prompt.txt").read_text(encoding="utf-8")
    return system_prompt, user_prompt


def _build_completion_request_params(*, question, context):
    system_prompt, user_prompt_template = _load_prompt_templates()
    user_prompt = user_prompt_template.format(context=context, question=question)
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    }


def perform_rag(user_query):
    embeddings = fetch_embeddings(user_query)
    semantic_search_result = perform_semantic_search(constants.QDRANT_COLLECTION_NAME, embeddings)

    if not semantic_search_result:
        return NO_INFO_MESSAGE

    context = [point.payload.get("content", "") for point in semantic_search_result]
    context = "\n".join(context)

    if not context.strip():
        return NO_INFO_MESSAGE

    request_params = _build_completion_request_params(question=user_query, context=context)
    return fetch_llm_response(request_params)
