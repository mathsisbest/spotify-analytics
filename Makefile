.PHONY: install lint format typecheck test precommit ci clean

install:
	pip install -e ".[dev]"

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

typecheck:
	mypy src/ tests/

test:
	pytest tests/ -v --cov=src

precommit:
	pre-commit run --all-files

ci: lint typecheck test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage
	rm -rf *.egg-info
