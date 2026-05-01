from types import SimpleNamespace

import lib.pipeline.rag as runtime


def test_perform_rag_returns_no_info_when_search_is_empty(monkeypatch):
    monkeypatch.setattr(runtime, "fetch_embeddings", lambda query: [0.1, 0.2])
    monkeypatch.setattr(runtime, "perform_semantic_search", lambda collection, embeddings: [])

    assert runtime.perform_rag("What is AI?") == runtime.NO_INFO_MESSAGE


def test_perform_rag_returns_no_info_when_context_is_blank(monkeypatch):
    points = [SimpleNamespace(payload={"content": "   "}), SimpleNamespace(payload={"content": ""})]
    monkeypatch.setattr(runtime, "fetch_embeddings", lambda query: [0.1, 0.2])
    monkeypatch.setattr(runtime, "perform_semantic_search", lambda collection, embeddings: points)

    assert runtime.perform_rag("What is AI?") == runtime.NO_INFO_MESSAGE


def test_perform_rag_builds_context_and_calls_completion(monkeypatch):
    points = [
        SimpleNamespace(payload={"content": "Context A"}),
        SimpleNamespace(payload={"content": "Context B"}),
    ]

    called = {}

    monkeypatch.setattr(runtime, "fetch_embeddings", lambda query: [0.3, 0.4])
    monkeypatch.setattr(runtime, "perform_semantic_search", lambda collection, embeddings: points)

    def fake_completion(request_params):
        called["request_params"] = request_params
        return "Final answer"

    monkeypatch.setattr(runtime, "fetch_llm_response", fake_completion)
    monkeypatch.setattr(runtime, "_build_completion_request_params", lambda question, context: {"messages": [{"role": "user", "content": context}], "question": question})

    assert runtime.perform_rag("What is AI?") == "Final answer"
    assert called == {
        "request_params": {"messages": [{"role": "user", "content": "Context A\nContext B"}], "question": "What is AI?"},
    }


def test_build_completion_request_params_loads_prompts_from_rag_directory(monkeypatch, tmp_path):
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "system_prompt.txt").write_text("system instructions", encoding="utf-8")
    (prompts_dir / "user_prompt.txt").write_text("context:\n{context}\nquestion:\n{question}", encoding="utf-8")
    monkeypatch.setattr(runtime, "PROMPTS_DIR", prompts_dir)

    request_params = runtime._build_completion_request_params(
        question="What is AI?",
        context="AI context",
    )

    assert request_params == {
        "messages": [
            {"role": "system", "content": "system instructions"},
            {"role": "user", "content": "context:\nAI context\nquestion:\nWhat is AI?"},
        ]
    }
