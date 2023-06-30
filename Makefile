all: install

.PHONY: clean
clean:
	@echo "clean :)"

.PHONY: install
install: clean
	pipx install .

.PHONY: uninstall
uninstall:
	pipx uninstall spex || true

.PHONY: check
check:
	./scripts/check.sh

.PHONY: format
format:
	./scripts/format.sh

.PHONY: docs
docs:
	cd docs && make all
