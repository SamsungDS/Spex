PROJECT_NAME = spex

# 'make' will list all documented targets
.DEFAULT_GOAL := help
.PHONY: help
help:
	@echo -e "\033[33mAvailable targets, for more information, see \033[36mREADME.md\033[0m"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: check
check:  ## (CI) run format-/lint-/import checks
	./scripts/check.sh

.PHONY: format
format: ## run formatters on code
	./scripts/format.sh

.PHONY: docs
docs: ## build documentation
	./scripts/mkdocs.sh

.PHONY: dev
dev: ## enter development environment (requires Nix)
	nix develop .#

