# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also from the
# environment for the first one (SPHINXOPTS)
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR      = source
BUILDDIR       = build
INDEX_PAGE	   = $(BUILDDIR)/html/index.html

.PHONY:
default: help
	@echo ""

.PHONY: open
open:
	@open $(INDEX_PAGE) || xdg-open $(INDEX_PAGE) || echo "!! Open $(INDEX_PAGE) in your browser to see the docs"

.PHONY: all
all: html open

.PHONY: help Makefile
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo ""
	@echo "or one of these additions to the 'sphinx-build' targets:"
	@echo "  open        to open HTML docs. ($(BUILDDIR)/html/index.html)"
	@echo "  all         to setup venv, build HTML docs and open them"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
