.. _sec-setup-nix:

Setting up Spex using Nix
=========================

.. note::
    In doubt as to which method to use when setting up Spex? See :ref:`sec-setup`.


Installing Nix
--------------
We would recommend following the instructions of the "Zero to Nix" guide
specificially the page on `installing nix`_.

.. note::
    If you install nix By other means,  be sure to enable flake support and the
    new CLI interface see NixOS Wiki Entry on `enabling flakes`_.


Using Spex
----------
This project provides a "Nix flake" which, broadly speaking, describes how to build
some software and how to configure a development environment. 

From within the Spex source directory, run ``nix develop .#`` to enter a
environment fully configured to run Spex.

From here, you may run spex using the command ``python -m spex`` and any arguments
you want. See ``python -m spex -h`` for what arguments Spex accepts.


.. _installing nix: https://zero-to-nix.com/start/install
.. _enabling flakes: https://nixos.wiki/wiki/Flakes#Enable_flakes
