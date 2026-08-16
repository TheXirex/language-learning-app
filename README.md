# language-learning-app

## Setup

```cmd
uv sync --all-groups
```

Make sure `.env` contains your MongoDB connection string (see `.env.example`):
```env
MONGODB_URI="your_mongodb_connection_string"
MONGODB_DB_NAME="language_learning"
MONGODB_COLLECTION_NAME="words"
```

## Running Tests

Run all tests:
```cmd
uv run pytest -v
```

Scrapper output is saved to `artifacts/scrapper/` (one JSON file per test word).
Test words are configured in `tests/test_config.py` (`SCRAPPER.test_inputs`).

