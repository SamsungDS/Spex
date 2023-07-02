.. _sec-setup:

Setting up Spex
===============

.. toctree::
   :maxdepth: 1
   :hidden:

   nix.rst
   docker.rst
   manual.rst


**spex** is implemented in Python and has the following dependencies for running it: 

1. Python >= 3.11 
    * **spex** relies on Python features for types introduced in Python 3.11
    
2. Python packages
    * For details, then have a look at the **Spex** package config (``setup.cfg``)

3. C libraries used by the Python packages
    * Specificaly, then **Spex** uses the Python package ``lxml`` which in turn
      requires the ``libxml2`` C library to be present on the system.


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

Nix
~~~

Development is done in an environment managed by ``nix`` which recreates
the *exact* same environment as is used for development and tests.

Unlike the other environments, this one is created each time you enter it
by running::

  nix develop .#

Which means the environment will always reflect changes to requirements such as
a newer version of Python or addition system (C) or Python dependencies.

Nix is the most comprehensive answer to the problem of "works on my machine"
yet. The downside is first needing to install Nix, and remembering that you must
first enter the environment by running the command ``nix develop .#`` prior
to running Spex.

Docker: nixenv
~~~~~~~~~~~~~~

Choose this if you are uncomfortable with Nix, but value using the same
reference environment as the developers.

Note that you should rebuild the Docker image on each new release, but
otherwise your environment should be as stable and tested as when using Nix.

The downside of using Docker is the complexity of Docker. Spex provides a
script which abstracts way some of this complexity (see
:ref:`sec-setup-docker`), but it is ultimately on you to operate this.

The benefit is the same reference environment and not having to install Nix
on your host machine.

Docker: debenv
~~~~~~~~~~~~~~

Manual
~~~~~~

If you are reasonably comfortable with Python virtual environments and
installing system libraries and alternative copies of Python, then manually
setting up Spex is just fine.

The benefit of this approach is needing neither Nix or Docker. But there is
no hand-holding with this approach. You will be required to infer the
dependencies needed from skimming the ``nix.flake`` and ``setup.cfg``
files, and to install the required components.

This is likely to be a sufficiently recent copy of the Python interpreter,
C libraries such as ``libxml2`` and the Python packages listed in the
above files.

Please note that dependencies may change and the only full, canonical specification
of what is required is described in the ``nix.flake`` file.

.. warning::
    As mentioned above - Spex reserves the right to update dependencies if it
    helps development or enables new features or better performance.
    
    If you choose the manual route, it is up to *you* to update your system
    accordingly.


