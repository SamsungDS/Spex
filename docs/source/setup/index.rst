.. _sec-setup:

Setting up Spex
===============

.. toctree::
   :maxdepth: 1
   :hidden:

   nix.rst
   docker.rst
   manual.rst

**Spex** is implemented in Python and distributed via :pypi:`Pypi <>` and thus
installable via ``pip``::

  pip install spex

And then run it::

  spex --help

For this to run then the following runtime requirements must be met:

1. Python >= 3.11 
    * **spex** relies on Python features for types introduced in Python 3.11
    
2. Python packages
    * For details, then have a look at the **Spex** package config (``setup.cfg``)

3. C libraries used by the Python packages
    * Specificaly, then **Spex** uses the Python package ``lxml`` which in turn
      requires the ``libxml2`` C library to be present on the system.

The setup of the above requirements is specific to the environment that you are
using. As a reference environment, then :nix:`Nix <>` 

.. note::
    **A note on Spex' requirements**
    
    Please note that these dependencies may change, and others may be added.
    The *only* exhaustive description of dependencies, is the ``flake.nix`` file.

    Please understand that dependencies are chosen and/or upgraded
    to make development easier, increase software robustness or provide
    additional features.
    Dependencies will not be dropped, nor will code be rewritten to support
    old software or conservative Linux distributions.
    
    You can use Nix or Docker to run on such platforms.

Which setup method to use?
--------------------------

You have 3 ways of setting up Spex:

1. **Nix**
2. **Docker**
3. **Manual (venv + system packages)**
