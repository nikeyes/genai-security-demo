.PHONY: default
default: lint

.PHONY: lint-fix
lint-fix:
	poetry run ruff format
	poetry run ruff check --fix-only 
	poetry run ruff check

.PHONY: lint
lint:
	poetry run ruff check

.PHONY: local-tests
test:
	poetry run pytest -v --cov=src --no-cov-on-fail --cov-report=term-missing tests/

.PHONY: ci-tests
test:
	poetry run pytest -v --cov=src --no-cov-on-fail --cov-report=term-missing tests/ -m "not real_provider"