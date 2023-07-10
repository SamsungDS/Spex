PROJECT_NAME = spex
DOCKER_IMAGE_NAME = $(PROJECT_NAME)-nixenv
DOCKER_IMAGE_TAG = latest
DOCKER_IMAGE_ID = ghcr.io/openmpdk/spex/$(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG)

all:
	@ $(MAKE) --no-print-directory all-msg
	@ $(MAKE) build

.PHONY: all-msg
all-msg:
	@echo -e "\033[33mmake invoked without any arguments, see \`\033[36mmake help\033[33m\` for a list of options\033[0m"

.PHONY: help
help:
	@echo -e "\033[33mAvailable targets, for more information, see \033[36mREADME.md\033[0m"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Build Spex source package (sdist)
	@python3 setup.py sdist

.PHONY: clean
clean: ## Remove artifacts from 'make build'
	@rm -r dist || echo "Nothing to remove/clean, this is ok."

.PHONY: install
install: build ## Install Spex using pipx and the source package (sdist)
	@pipx install dist/nvme-$(PROJECT_NAME)*.tar.gz

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

.PHONY: dev
dev: ## enter development environment (requires Nix)
	nix develop .#

.PHONY: dev-docker-build
dev-docker-build:  ## build development environment as a docker container
	docker build \
	. \
	-f docker/nixenv/Dockerfile \
	-t $(DOCKER_IMAGE_ID)

.PHONY: dev-docker
dev-docker: ## enter containerized development environment
	docker run \
	--rm \
	-it \
	-w /tmp/$(PROJECT_NAME) \
	--mount type=bind,source="$(shell pwd)",target=/tmp/$(PROJECT_NAME) \
	$(DOCKER_IMAGE_ID) \
	nix develop .#
