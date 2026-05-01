from invoke.tasks import task
from invoke.collection import Collection
from app.config import constants
from qdrant_client.http import models
from lib.clients.qdrant import get_qdrant_client
from lib.pipeline.ingestion import start_data_injection

@task
def create_qdrant_collection(ctx):
    client = get_qdrant_client()
    client.create_collection(
        collection_name=constants.QDRANT_COLLECTION_NAME,
        vectors_config={"size": 3072, "distance": models.Distance.COSINE, "on_disk": True}
    )

@task
def delete_qdrant_collection(ctx):
    client = get_qdrant_client()
    client.delete_collection(
        collection_name=constants.QDRANT_COLLECTION_NAME
    )

@task
def populate_qdrant_collection(ctx):
    start_data_injection()

one_time_collection = Collection('one-time-tasks')
one_time_collection.add_task(create_qdrant_collection, 'create-qdrant-collection')
one_time_collection.add_task(delete_qdrant_collection, 'delete-qdrant-collection')
one_time_collection.add_task(populate_qdrant_collection, 'populate-qdrant-collection')
