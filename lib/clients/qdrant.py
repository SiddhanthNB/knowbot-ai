from qdrant_client import QdrantClient

from app.config import constants

_client = QdrantClient(url=constants.QDRANT_URL, api_key=constants.QDRANT_ACCESS_KEY)


def get_qdrant_client():
    return _client

def _check_collection_exists(collection_name):
    if not _client.collection_exists(collection_name=collection_name):
        raise Exception(f"Collection '{collection_name}' does not exist.")

def perform_semantic_search(collection_name, query_vector, top_k=5, score_threshold=0.7):
    _check_collection_exists(collection_name)

    return _client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        with_payload=True,
        with_vectors=False,
        score_threshold=score_threshold,
        offset=0,
        limit=top_k
    )
