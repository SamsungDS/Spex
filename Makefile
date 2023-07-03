PROJECT_NAME = spex

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
	./scripts/mkdocs.sh
