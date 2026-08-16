# language-learning-app

## Test pipeline

```cmd
uv sync --all-groups
uv run pytest tests/test_scrapper_pipeline.py -v
```

Output is saved to `artifacts/scrapper/` (one JSON file per test word).

Test words are configured in `tests/test_config.py` (`SCRAPPER.test_inputs`).
