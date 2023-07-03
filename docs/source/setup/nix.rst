.. _sec-setup-nix:

Settings up Spex with Nix
=========================

Development is done in an environment managed by ``nix`` which recreates the
*exact* same environment as is used for running, developing and testing
**Spex**. To create the environment, then you need to install ``nix``

Install Nix
-----------
Skip this section if you have already installed Nix.

Linux & MacOS
~~~~~~~~~~~~~

On Linux and MacOS, run the following to install nix::

  curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install


Windows (WSL)
~~~~~~~~~~~~~
Windows can use Nix through the Windows Subsystem for Linux (WSL) environment.

First install WSL. Open a command-prompt and type::

  wsl --install

You may have to reboot the machine afterwards.

Then install a Ubuntu WSL VM::

  wsl --install -d ubuntu


Then, from *within the WSL environment* (type ``wsl`` in command-prompt to enter), install Nix in *single-user mode*::

  sh <(curl -L https://nixos.org/nix/install) --no-daemon


Finally, close your command prompt(s) and start a new one, now Nix should be installed and ready for use!


Using the development environment
---------------------------------
Then drop into the :nix:`Nix <>` development environment::

  nix develop .#

... now you can run spex like so::

  python -m spex

See ``python -m spex -h`` for what arguments **Spex** accepts and
:ref:`sec-using-spex` for details on using Spex.


Unlike the other environments, this one is created each time you enter it by
running.

Which means the environment will always reflect changes to requirements such as
a newer version of Python or addition system (C) or Python dependencies.

Nix is the most comprehensive answer to the problem of "works on my machine"
yet. The downside is first needing to install Nix, and remembering that you must
first enter the environment by running the command ``nix develop .#`` prior
to running Spex.

