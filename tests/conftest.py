from pathlib import Path

import pytest

from test_config import ModuleTestConfig, SCRAPPER


@pytest.fixture
def scrapper_config() -> ModuleTestConfig:
    return SCRAPPER


@pytest.fixture
def artifacts_dir(scrapper_config: ModuleTestConfig) -> Path:
    scrapper_config.artifacts_dir.mkdir(parents=True, exist_ok=True)
    return scrapper_config.artifacts_dir
