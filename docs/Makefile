# Minimal makefile for Sphinx documentation
#

# Build documentation in a Python venv
VENV		= . venv/bin/activate && 
PYTHON		= $(VENV) python3
PYTHON_SYS	= python3

# You can set these variables from the command line, and also from the
# environment for the first one (SPHINXOPTS)
SPHINXOPTS    ?=
SPHINXBUILD   = $(VENV) sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

.PHONY:
default: venv help
	@echo ""

venv:
	@$(PYTHON_SYS) -m venv venv
	@$(PYTHON) -m pip install -r requirements.txt

.PHONY: open
open:
	@open $(BUILDDIR)/html/index.html || xdg-open $(BUILDDIR)/html/index.html || echo "!! Open $(BUILDDIR)/html/index.html in your browser to see the docs"

.PHONY: all
all: venv html open

.PHONY: help Makefile
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo ""
	@echo "or one of these additions to the 'sphinx-build' targets:"
	@echo "  default     to run 'venv' then 'help'"
	@echo "  venv        to setup a Python venv. using requirements.txt"
	@echo "  open        to open HTML docs. ($(BUILDDIR)/html/index.html)"
	@echo "  all         to setup venv, build HTML docs and open them"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
