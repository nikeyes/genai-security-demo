help: ## Show help
	@echo Please specify a build target. The choices are:
	@echo ""
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo For more information: https://pages.github.mpi-internal.com/unicron/kfp-minimal-template/sample_develop/#running-the-pipeline-using-kubeflow-pipelines

.PHONY: python-lint
python-lint:
	ruff format
	ruff check --fix-only 
	ruff check
