# Resonance (Spotify Analytics) — Project Profile

## Stack
Python 3.11, BigQuery, dbt-bigquery, scikit-learn, Streamlit, pytest, ruff, mypy

## Gate
```bash
make install  # pip install -e ".[dev]"
make ci       # ruff check → mypy → pytest
```

## Velocity pattern
See `AGENTS.md` for the per-wave workflow. Default: Sonnet for implementation, human reviews all PRs before merge.

## Key conventions
- No comments in code unless unavoidable
- Type-annotated everything (mypy strict)
- Tests in `tests/test_<module>.py`, one class per function/concern
- ML models are stateless functions, not classes
- Feature vectors are `list[dict[str, Any]]`
- Train pipeline is CLI-driven: `python -m ml.train --mode <cluster|predict|forecast>`
