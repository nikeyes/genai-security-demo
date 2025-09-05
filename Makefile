.PHONY: default
default: lint

.PHONY: install
install:
# 	uv cache clean
# 	rm -r "$(uv python dir)"
# 	rm -r "$(uv tool dir)"
# 	rm ~/.local/bin/uv ~/.local/bin/uvx
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	uv sync --all-extras

.PHONY: lint-fix
lint-fix:
	uv run ruff format
	uv run ruff check --fix-only 
	uv run ruff check

.PHONY: lint
lint:
	uv run ruff check

.PHONY: local-tests
local-tests:
	uv run pytest -v --cov=src --no-cov-on-fail --cov-report=term-missing tests/

.PHONY: ci-tests
ci-tests:
	uv run pytest -v --cov=src --no-cov-on-fail --cov-report=term-missing tests/ -m "not real_provider"