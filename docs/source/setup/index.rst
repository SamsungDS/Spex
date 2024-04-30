.. _sec-setup:

Setting up Spex
===============

.. toctree::
   :maxdepth: 1
   :hidden:

   nix.rst
   manual.rst

**Spex** has various dependencies. You can use :ref:`sec-setup-nix` to setup the reference
environment which is actively used in development and tested in CI.

Otherwise, you can install Spex in the traditional way, see :ref:`sec-setup-manual`.

.. note::
    **A note on Spex' requirements**
    
    Please note that these dependencies may change, and others may be added.
    The *only* exhaustive description of dependencies, is the ``flake.nix`` file.

    Please understand that dependencies are chosen and/or upgraded
    to make development easier, increase software robustness or provide
    additional features.
    Dependencies will not be dropped, nor will code be rewritten to support
    old software or conservative Linux distributions.
    
    You can use Nix to run on such platforms.
