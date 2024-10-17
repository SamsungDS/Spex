.. _sec-setup-nix:

Setting up Spex with Nix
=========================

Development is done in an environment managed by ``nix`` which recreates the
*exact* same environment as is used for running, developing and testing
**Spex**. To create the environment, you need to install ``nix``.

Using the Nix environment
-------------------------
If you have not yet installed nix, see :ref:`sec-setup-nix-install` below.

Run Spex (development)
~~~~~~~~~~~~~~~~~~~~~~
To run Spex in a development context, where unversioned local changes are taken into account:

Enter the development environment::

  nix develop .#

Run spex::

  spex

.. note::
  The ``spex`` command is actually an alias defined in the shell described by ``flake.nix``, which modifies
  the ``PYTHONPATH`` variable to put the ``./src`` directory on ``sys.path``, where modules are searched, and
  the ``-m`` flag to execute the ``spex`` module.

  This means ``spex`` uses the local source code files, and any changes made to the source will be reflected
  next time you run ``spex``. However, it also *requires* you to stand in the project root (or ``src``) directory.

  For details on how executable modules work and the ``python -m <module>`` command, see
  `Python docs on __main__.py in Python Packages <https://docs.python.org/3/library/__main__.html#main-py-in-python-packages>`_ for details.

Now run ``spex -h`` (or just ``spex`` without arguments) to see which arguments you can provide.
For information on using Spex, see :ref:`sec-using-spex`.

Run the Spex program
~~~~~~~~~~~~~~~~~~~~
You can run spex, even without cloning the repository, like so::

  nix run github:SamsungDS/Spex#spex

.. note::
  that this is not for development use, this will not reflect any local changes made to the source code.

.. _sec-setup-nix-install:

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

