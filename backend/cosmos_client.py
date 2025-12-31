import os
from azure.cosmos import CosmosClient

_client = None
_database = None

def get_container(container_name: str):
    global _client, _database

    if _client is None:
        endpoint = os.getenv("COSMOS_ENDPOINT")
        key = os.getenv("COSMOS_KEY")
        db_name = os.getenv("COSMOS_DB_NAME")

        _client = CosmosClient(endpoint, key)
        _database = _client.get_database_client(db_name)

    return _database.get_container_client(container_name)
