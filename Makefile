# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

PROJECT_NAME = spex

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo -e "\033[33mAvailable targets, for more information, see \033[36mREADME.md\033[0m"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Build Spex source package (sdist)
	@python3 -m build

.PHONY: clean
clean: ## Remove artifacts from 'make build'
	@rm -r dist || echo "Nothing to remove/clean, this is ok."

.PHONY: install
install: build ## Install Spex using pipx and the source package (sdist)
	@pipx install dist/nvme_$(PROJECT_NAME)*.tar.gz

.PHONY: uninstall
uninstall: ## Uninstall Spex using pipx
	@pipx uninstall $(PROJECT_NAME) || echo "Nothing to uninstall, that is ok."

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

.PHONY: runserver
runserver: ## Start the spexsrv webapplication
	PYTHONPATH=./src:$PYTHONPATH python3 src/spexsrv/__main__.py
