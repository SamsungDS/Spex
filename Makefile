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

#
# magic: Bringing it together end-to-end prototype
#
# * spex: .docx to .html + .json
# * spex_to_yace: .json to .yaml
# * yace: output C API etc.
#
magic: clean spex custom yace

spex:
	spex input/{nvm,zns}.docx --output builddir

custom:
	python3 scripts/spex_to_yace.py

yace:
	yace builddir/foo.yaml --emit npapi -l
