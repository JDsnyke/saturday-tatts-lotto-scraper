# Contributing

Contributions are welcome. The project values mathematical accuracy, data integrity and restrained claims over “prediction” features.

## Development setup

```bash
python3 -m pip install -r requirements-dev.txt
export PYTHONPATH="$PWD/src"
python3 -m unittest discover -s tests -v
ruff check src tests
```

## Principles

1. Do not turn historical frequency, recency or pair counts into claimed future draw probability without rigorous evidence of non-randomness.
2. Keep descriptive diagnostics and ticket-generation policy separate.
3. Add tests for parser, probability or generator changes.
4. Prefer deterministic fixtures and seeded simulations in tests.
5. Scraper changes should remain polite to the source site and avoid unnecessary requests.
6. UI changes must remain keyboard usable and respect `prefers-reduced-motion`.

## Pull requests

Keep pull requests focused, explain the statistical or engineering rationale, and include the commands used to test the change. Update `ROADMAP.md` when a tracked item is completed or materially re-scoped.
