# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Spex"
copyright = "2023 Samsung Electronics Co., Ltd"
author = "Jesper Wendel Devantier"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.extlinks", "sphinx_copybutton"]

templates_path = ["_templates"]
exclude_patterns = []

extlinks = {
    "html": ("https://en.wikipedia.org/wiki/HTML%s", None),
    "json": ("https://www.json.org/%s", None),
    "json-schema": ("https://json-schema.org/%s", None),
    "nix": ("https://nixos.org/%s", None),
    "nix-flakes": ("https://nixos.wiki/wiki/Flakes#Enable_flakes%s", None),
    "nix-install": ("https://zero-to-nix.com/start/install/%s", None),
    "nix-install-windows": (
        "https://nixos.org/download.html#nix-install-windows%s",
        None,
    ),
    "nvme": ("https://nvmexpress.org/%s", None),
    "nvme-lint": ("https://github.com/linux-nvme/nvme-lint/%s", None),
    "nvme-lint-post": (
        "https://nvmexpress.org/nvme-lint-new-open-source-tool-to-help-validate-the-nvm-express-specifications/%s",
        None,
    ),
    "nvme-specs": ("https://nvmexpress.org/specifications/%s", None),
    "pipx": ("https://pypa.github.io/pipx/%s", None),
    "pypi": ("https://pypi.org/%s", None),
    "repos-blob": ("https://github.com/OpenMPDK/Spex/blob/main/%s", None),
    "repos-actions": ("https://github.com/OpenMPDK/Spex/actions/workflows/example.yml%s", None)
}

# -- Optins for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

html_css_files = ["css/custom.css"]
html_js_files = ["scripts/custom.js"]
html_extra_path = ["_static/spex.py"]
