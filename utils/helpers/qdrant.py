from config.qdrant import get_qdrant_client

_client = get_qdrant_client()

def _check_collection_exists(collection_name):
    if not _client.collection_exists(collection_name=collection_name):
        raise Exception(f"Collection '{collection_name}' does not exist.")

def perform_semantic_search(collection_name, query_vector, top_k=10):
    _check_collection_exists(collection_name)

    return _client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        with_payload=True,
        with_vectors=False,
        score_threshold=0.7,
        offset=0,
        limit=top_k
    )
