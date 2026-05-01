import requests
import utils.constants as constants

CORENEST_EMBEDDINGS_PROVIDER = "google"


def _build_headers():
    return {"Authorization": f"Bearer {constants.CORENEST_SECRET_KEY}"}


def _dispatch_request(url="", method="get", params=None, headers=None):
    if url.strip() == "":
        raise ValueError("URL cannot be empty")

    method = method.lower()
    params = params or {}
    headers = headers or {}

    if method not in ["get", "post"]:
        raise ValueError(f"Unsupported HTTP method: {method}")

    response = requests.__dict__[method](url, json=params, headers=headers)
    response.raise_for_status()
    return response.json()


def _extract_embedding(response):
    try:
        return response["data"][0]["embedding"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("Unexpected embeddings response format from CoreNest") from exc


def _extract_completion_text(response):
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("Unexpected completions response format from CoreNest") from exc

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str):
                text_parts.append(item["text"])
        if text_parts:
            return "".join(text_parts)

    raise ValueError("Unsupported completion content format from CoreNest")


def perform_ping():
    url = f"{constants.CORENEST_API_URL}/ping"
    response = _dispatch_request(url)
    return response == "pong"


def fetch_embeddings(text):
    url = f"{constants.CORENEST_API_URL}/embeddings"
    headers = _build_headers()
    headers["X-LLM-Provider"] = CORENEST_EMBEDDINGS_PROVIDER
    params = {"input": [text]}
    response = _dispatch_request(url, "post", params, headers)
    return _extract_embedding(response)


def fetch_llm_response(question, context):
    url = f"{constants.CORENEST_API_URL}/completions"

    with open("utils/prompts/system_prompt.txt", "r") as system_prompt_file:
        system_prompt = system_prompt_file.read()

    with open("utils/prompts/user_prompt.txt", "r") as user_prompt_file:
        user_prompt = user_prompt_file.read()

    user_prompt = user_prompt.format(context=context, question=question)
    params = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    }
    response = _dispatch_request(url, "post", params, _build_headers())
    return _extract_completion_text(response)
