import pytest

from lib.clients import qdrant


class _FakeClient:
    def __init__(self, *, exists=True, search_result=None):
        self.exists = exists
        self.search_result = search_result or []
        self.search_calls = []

    def collection_exists(self, *, collection_name):
        return self.exists

    def search(self, **kwargs):
        self.search_calls.append(kwargs)
        return self.search_result


def test_check_collection_exists_raises_when_missing(monkeypatch):
    monkeypatch.setattr(qdrant, "_client", _FakeClient(exists=False))

    with pytest.raises(Exception, match="does not exist"):
        qdrant._check_collection_exists("kb")


def test_perform_semantic_search_uses_configured_client(monkeypatch):
    fake_client = _FakeClient(exists=True, search_result=[{"id": 1}])
    monkeypatch.setattr(qdrant, "_client", fake_client)

    result = qdrant.perform_semantic_search("kb", [0.1, 0.2], top_k=3, score_threshold=0.8)

    assert result == [{"id": 1}]
    assert fake_client.search_calls == [
        {
            "collection_name": "kb",
            "query_vector": [0.1, 0.2],
            "with_payload": True,
            "with_vectors": False,
            "score_threshold": 0.8,
            "offset": 0,
            "limit": 3,
        }
    ]
