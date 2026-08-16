from datetime import datetime, timezone
from typing import Any
from pymongo.collection import Collection
from pymongo import ASCENDING

from modules.db.client import get_collection


class WordRepository:
    """Repository for managing word documents in MongoDB."""

    def __init__(self, collection: Collection | None = None):
        self._collection = collection if collection is not None else get_collection()
        self._ensure_indexes()

    @property
    def collection(self) -> Collection:
        return self._collection

    def _ensure_indexes(self) -> None:
        """Create indexes if they do not exist."""
        self._collection.create_index([("word", ASCENDING)], unique=True)

    def save_word(self, word_data: dict[str, Any]) -> dict[str, Any]:
        """
        Upsert a word document into MongoDB.
        
        If the word document exists, updates its fields and 'updated_at' timestamp.
        If it does not exist, inserts it and sets 'created_at' and 'updated_at'.
        """
        if not word_data or not word_data.get("word"):
            raise ValueError("Invalid word_data: 'word' key is required and cannot be empty.")

        now = datetime.now(timezone.utc)
        word_key = word_data["word"]

        payload = {k: v for k, v in word_data.items() if k != "_id"}
        payload["updated_at"] = now

        self._collection.update_one(
            {"word": word_key},
            {
                "$set": payload,
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )

        return self.get_word(word_key)

    def get_word(self, word: str) -> dict[str, Any] | None:
        """Retrieve word document by word string."""
        return self._collection.find_one({"word": word})

    def list_words(self, limit: int = 100, skip: int = 0) -> list[dict[str, Any]]:
        """List stored words with pagination."""
        return list(self._collection.find().skip(skip).limit(limit))

    def delete_word(self, word: str) -> bool:
        """Delete word document by word string."""
        result = self._collection.delete_one({"word": word})
        return result.deleted_count > 0
