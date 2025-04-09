import utils.constants as constants
from qdrant_client import QdrantClient

_client = QdrantClient(url=constants.QDRANT_URL, api_key=constants.QDRANT_ACCESS_KEY)

def get_qdrant_client():
    return _client
