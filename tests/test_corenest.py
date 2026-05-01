from unittest.mock import MagicMock

from lib.clients import corenest


def test_perform_ping_uses_ping_endpoint(monkeypatch):
    response = MagicMock()
    response.json.return_value = "pong"

    def fake_get(url, json, headers):
        assert url == "https://core-nest.example/ping"
        assert json == {}
        assert headers == {}
        return response

    corenest.constants.CORENEST_API_URL = "https://core-nest.example"
    monkeypatch.setattr(corenest.requests, "get", fake_get)

    assert corenest.perform_ping() is True
    response.raise_for_status.assert_called_once_with()


def test_fetch_embeddings_uses_input_payload_and_provider_header(monkeypatch):
    response = MagicMock()
    response.json.return_value = {
        "object": "list",
        "data": [{"embedding": [0.1, 0.2, 0.3], "index": 0}],
        "model": "text-embedding-3-small",
    }

    def fake_post(url, json, headers):
        assert url == "https://core-nest.example/embeddings"
        assert json == {"input": ["hello world"]}
        assert headers == {
            "Authorization": "Bearer secret-key",
            "X-LLM-Provider": corenest.CORENEST_EMBEDDINGS_PROVIDER,
        }
        return response

    corenest.constants.CORENEST_API_URL = "https://core-nest.example"
    corenest.constants.CORENEST_SECRET_KEY = "secret-key"
    monkeypatch.setattr(corenest.requests, "post", fake_post)

    assert corenest.fetch_embeddings("hello world") == [0.1, 0.2, 0.3]
    response.raise_for_status.assert_called_once_with()


def test_fetch_llm_response_uses_messages_payload(monkeypatch):
    response = MagicMock()
    response.json.return_value = {
        "id": "cmpl_1",
        "object": "chat.completion",
        "choices": [{"message": {"content": "Answer text"}}],
    }
    request_params = {
        "messages": [
            {"role": "system", "content": "system instructions"},
            {"role": "user", "content": "context:\nAI context\nquestion:\nWhat is AI?"},
        ]
    }

    def fake_post(url, json, headers):
        assert url == "https://core-nest.example/completions"
        assert json == request_params
        assert headers == {"Authorization": "Bearer secret-key"}
        return response

    corenest.constants.CORENEST_API_URL = "https://core-nest.example"
    corenest.constants.CORENEST_SECRET_KEY = "secret-key"
    monkeypatch.setattr(corenest.requests, "post", fake_post)

    assert corenest.fetch_llm_response(request_params) == "Answer text"
    response.raise_for_status.assert_called_once_with()


def test_extract_completion_text_supports_text_content_blocks():
    content = corenest._extract_completion_text(
        {
            "choices": [
                {
                    "message": {
                        "content": [
                            {"type": "text", "text": "Hello"},
                            {"type": "input_text", "text": "ignored"},
                            {"type": "text", "text": " world"},
                        ]
                    }
                }
            ]
        }
    )

    assert content == "Hello world"
