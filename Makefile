PROJECT_NAME = spex
DOCKER_IMAGE_NAME = $(PROJECT_NAME)-debenv
DOCKER_IMAGE_TAG = latest
DOCKER_IMAGE_ID = ghcr.io/openmpdk/spex/$(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG)

all: uninstall install

.PHONY: clean
clean:
	@echo "clean :)"

.PHONY: install
install: clean
	pipx install .

.PHONY: uninstall
uninstall:
	pipx uninstall $(PROJECT_NAME) || true

.PHONY: check
check:
	./scripts/check.sh

.PHONY: format
format:
	./scripts/format.sh

.PHONY: docs
docs:
	cd docs && make all

.PHONY: docker-build
docker-build:
	docker build \
	. \
	-f docker/debian/Dockerfile \
	-t $(DOCKER_IMAGE_ID)

.PHONY: docker-push
docker-push:
	docker push $(DOCKER_IMAGE_ID)

.PHONY: docker
docker:
	docker run \
	-it \
	-w /tmp/$(PROJECT_NAME) \
	--mount type=bind,source="$(shell pwd)",target=/tmp/$(PROJECT_NAME) \
	$(DOCKER_IMAGE_ID) \
	/bin/bash
