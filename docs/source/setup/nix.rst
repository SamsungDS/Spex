.. _sec-setup-nix:

Nix
===

Development is done in an environment managed by ``nix`` which recreates the
*exact* same environment as is used for running, developing and testing
**Spex**. To create the environment, then you need to install ``nix``, on Linux
and MacOS::

  curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install

.. note:
   For Windows, then have a closer look at the :nix-install-windows:`https://nixos.org/download.html#nix-install-windows`

Then drop into the :nix:`Nix <>` development environment::

  nix develop .#

foo bar::

  python -m spex

See ``python -m spex -h`` for what arguments **Spex** accepts.

Unlike the other environments, this one is created each time you enter it by
running.

Which means the environment will always reflect changes to requirements such as
a newer version of Python or addition system (C) or Python dependencies.

Nix is the most comprehensive answer to the problem of "works on my machine"
yet. The downside is first needing to install Nix, and remembering that you must
first enter the environment by running the command ``nix develop .#`` prior
to running Spex.

Installing Nix
--------------

We would recommend following the instructions of the "Zero to Nix" guide
specificially the page on :nix-install:`installing nix <>`

.. note::
   If you install nix By other means,  be sure to enable flake support and the
   new CLI interface see NixOS Wiki Entry on :nix-flakes:`enabling flakes <>`.

In case you cannot install :nix:`Nix <>` then you can use Docker to bring of
the :nix:`Nix <>` environment.


Using Spex
----------

This project provides a "Nix flake" which, broadly speaking, describes how to
build some software and how to configure a development environment. 

From within the **Spex** source directory, run::

  nix develop .#

o enter a environment fully configured to run **Spex**.

From here, you may run spex using the command::

  python -m spex

and any arguments you want. 
