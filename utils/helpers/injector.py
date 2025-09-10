import re, time, wikipedia, uuid
from config.logger import logger
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
import utils.constants as constants
from config.qdrant import get_qdrant_client
from utils.helpers.qdrant import _check_collection_exists
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
from langchain_google_genai._common import GoogleGenerativeAIError
from utils.helpers.topics_list import WIKIPEDIA_TOPICS

def _load_wikipedia_articles():
    topics_to_process = list(WIKIPEDIA_TOPICS)
    all_articles = []
    loaded_topics = set()

    for topic in topics_to_process:
        if topic in loaded_topics:
            continue
        try:
            logger.info(f"Loading wikipedia article for topic: {topic}")
            article = wikipedia.page(topic, auto_suggest=False)
            all_articles.append(article)
            loaded_topics.add(topic)
        except Exception as e:
            logger.error(f"Failed to load document for topic: {topic}. Error: {e}")

    return all_articles


HEADING_PATTERN = re.compile(r"^\s*(#+|=+)\s*.*\s*(#+|=+)?\s*$")

def _is_low_value_chunk(text):
    """
    Checks if a text chunk is low-value for embedding purposes.
    This includes gibberish, very short text, or standalone headings.
    """
    stripped_text = text.strip()

    # 1. Filter out very short chunks
    if len(stripped_text.split()) < 5:
        return True

    # 2. Filter out chunks that are ONLY headings
    if HEADING_PATTERN.match(stripped_text):
        if len(stripped_text.split()) < 10:
            return True

    # 3. Keep the existing check for a high ratio of non-alphanumeric characters
    alpha_count = sum(c.isalpha() for c in stripped_text)
    if len(stripped_text) > 0 and alpha_count / len(stripped_text) < 0.5:
        return True

    # 4. Keep the existing language detection to filter actual gibberish
    try:
        detect(stripped_text)
    except LangDetectException:
        return True

    return False


@retry(
    wait=wait_random_exponential(min=2, max=60),
    stop=stop_after_attempt(5),
    retry_error_callback=lambda retry_state: logger.error(f"Failed to embed chunks after multiple retries: {retry_state.outcome.exception()}"),
    retry=retry_if_exception_type(GoogleGenerativeAIError)
)
def _get_embeddings(embedding_model, chunks):
    """Wrapper to embed documents with retry logic."""
    logger.info(f"Attempting to embed {len(chunks)} document chunks...")
    return embedding_model.embed_documents(chunks)


def _process_article_content(article, client: QdrantClient):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000, chunk_overlap=400, separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_text(article.content)
    logger.info(f"Article '{article.title}' split into {len(chunks)} chunks.")

    clean_chunks = [c for c in chunks if not _is_low_value_chunk(c)]

    points = []
    batch_size = 250
    embedding_model = GoogleGenerativeAIEmbeddings(
        model=f"{constants.GOOGLE_EMBEDDING_MODEL}",
        google_api_key=constants.GOOGLE_API_KEY,
    )

    for i in range(0, len(clean_chunks), batch_size):
        batch_chunks = clean_chunks[i : i + batch_size]

        embeddings = _get_embeddings(embedding_model, batch_chunks)

        if not embeddings or len(embeddings) != len(batch_chunks):
            logger.error(f"Embedding failed for a batch in article '{article.title}'. Skipping this batch.")
            continue

        for j, chunk in enumerate(batch_chunks):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embeddings[j],
                payload={
                    "source": "wikipedia",
                    "title": article.title,
                    "url": article.url,
                    "content": chunk,
                },
            )
            points.append(point)

    if points:
        client.upsert(collection_name=constants.QDRANT_COLLECTION_NAME, points=points, wait=True)
        logger.info(f"Upserted {len(points)} points for article '{article.title}'.")
    else:
        logger.info(f"No points to upsert for article '{article.title}'.")


def start_data_injection():
    logger.info("Starting data injection script...")

    _check_collection_exists(constants.QDRANT_COLLECTION_NAME)
    client = get_qdrant_client()

    articles = _load_wikipedia_articles()

    for i, article in enumerate(articles):
        logger.info(f"Processing article {i+1}/{len(articles)}: {article.title}")
        _process_article_content(article, client)
        logger.info("Waiting for 15 seconds before processing next article...")
        time.sleep(15)

    logger.info("Data injection script finished.")
