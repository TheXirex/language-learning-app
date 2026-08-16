from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from modules.db.settings import DBSettings, get_db_settings


def get_mongo_client(uri: str | None = None, **kwargs) -> MongoClient:
    """Create and return a PyMongo client instance."""
    settings = get_db_settings()
    mongo_uri = settings.uri if uri is None else uri
    if not mongo_uri:
        raise ValueError("MongoDB URI is required. Please set MONGODB_URI in your environment or .env file.")
    return MongoClient(mongo_uri, **kwargs)


def get_database(
    client: MongoClient | None = None,
    db_name: str | None = None,
    settings: DBSettings | None = None,
) -> Database:
    """Get database from client or create a new client."""
    current_settings = settings or get_db_settings()
    client = client or get_mongo_client(current_settings.uri)
    target_db = db_name or current_settings.db_name
    return client[target_db]


def get_collection(
    client: MongoClient | None = None,
    db_name: str | None = None,
    collection_name: str | None = None,
    settings: DBSettings | None = None,
) -> Collection:
    """Get collection from database."""
    current_settings = settings or get_db_settings()
    db = get_database(client, db_name, current_settings)
    target_col = collection_name or current_settings.collection_name
    return db[target_col]
