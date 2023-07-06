PROJECT_NAME = spex

# 'make' will list all documented targets
.DEFAULT_GOAL := build
.PHONY: help
help:
	@echo -e "\033[33mAvailable targets, for more information, see \033[36mREADME.md\033[0m"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Build Spex source package (sdist)
	@python3 setup.py sdist

.PHONY: clean
clean: ## Remove artifacts from 'make build'
	@rm -r dist || echo "Nothing to remove/clean, this is ok."

.PHONY: install
install: build ## Install Spex using pipx and the source package (sdist)
	@pipx install dist/$(PROJECT_NAME)*.tar.gz

.PHONY: uninstall
uninstall: ## Uninstall Spex using pipx
	@pipx uninstall spex || echo "Nothing to uninstall, that is ok."

.PHONY: check
check:  ## (CI) run format-/lint-/import checks
	./scripts/check.sh

.PHONY: format
format: ## run formatters on code
	./scripts/format.sh

.PHONY: docs
docs: ## build documentation
	./scripts/mkdocs.sh
