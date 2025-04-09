import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_NAME = os.getenv('CLIENT_NAME')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

CORENEST_API_URL = os.getenv('CORENEST_API_URL')

QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME')
QDRANT_ACCESS_KEY = os.getenv('QDRANT_ACCESS_KEY')
