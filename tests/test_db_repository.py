import pytest

from modules.db import WordRepository
from modules.scrapper import run_spider
from test_config import SCRAPPER


@pytest.mark.parametrize("word", SCRAPPER.test_inputs)
def test_save_word_to_db(word: str) -> None:
    # 1. Process word via scrapper
    word_data = run_spider(word)
    assert word_data, f"No data extracted for word '{word}'"

    # 2. Save extracted word data to MongoDB using environment credentials
    repo = WordRepository()
    saved = repo.save_word(word_data)

    assert saved is not None
    assert saved["word"] == word_data["word"]
    assert "created_at" in saved
    assert "updated_at" in saved
    assert len(saved["definitions"]) > 0

    # 3. Verify retrieval from database
    fetched = repo.get_word(word_data["word"])
    assert fetched is not None
    assert fetched["word"] == word_data["word"]
    assert fetched["url"] == word_data["url"]
