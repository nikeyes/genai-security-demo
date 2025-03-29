.PHONY: default
default: lint

.PHONY: lint
lint:
	poetry run ruff format
	poetry run ruff check --fix-only 
	poetry run ruff check

.PHONY: test
test:
	poetry run pytest -v --cov=src --no-cov-on-fail --cov-report=term-missing tests/