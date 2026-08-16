import json
from pathlib import Path

import pytest

from scrapper import run_spider
from test_config import SCRAPPER


@pytest.mark.parametrize("word", SCRAPPER.test_inputs)
def test_word_extraction_pipeline(word: str, artifacts_dir: Path) -> None:
    result = run_spider(word)

    assert result, f"No data extracted for word '{word}'"
    assert result.get("word"), "Extracted result must contain 'word'"
    assert result.get("url"), "Extracted result must contain 'url'"
    assert isinstance(result.get("definitions"), list), "'definitions' must be a list"

    for definition in result["definitions"]:
        assert "definition" in definition
        assert "examples" in definition
        assert isinstance(definition["examples"], list)

    output_path = artifacts_dir / f"{word}.json"
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
