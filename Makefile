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
