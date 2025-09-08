import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv('APP_ENV', 'production')

CORENEST_API_URL = os.getenv('CORENEST_API_URL')
CORENEST_SECRET_KEY = os.getenv('CORENEST_SECRET_KEY')

QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME')
QDRANT_ACCESS_KEY = os.getenv('QDRANT_ACCESS_KEY')
