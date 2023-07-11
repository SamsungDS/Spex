.. _sec-setup-docker:

Setting up Spex using Docker
============================

.. note::
    In doubt as to which method to use when setting up Spex? See :ref:`sec-setup`.


As a *user* of Spex
-------------------
The Spex project publishes a Docker image for running Spex. We also provide a wrapper script
which abstracts away the complexities of mapping files into and out of the Docker container.
Download the Spex script like so::

    curl --proto '=https' --tlsv1.2 -sSf -L https://openmpdk.github.io/Spex/_static/spex.py -o spex.py

.. note::
    **If you don't have CURL**: Visit the link https://openmpdk.github.io/Spex/_static/spex.py
    and download the script manually.


To run Spex, simply execute the script like so::

    python spex.py

See :ref:`sec-using-spex` for details on using Spex.

.. note::
    **Which version of Spex is used?**
    The wrapper script will always use the latest (development) version.
    Please visit https://github.com/OpenMPDK/Spex/pkgs/container/spex/versions
    and pick a version tag suiting your use-case, then run spex like so::

        python spex.py --tag=VERSION


As a *developer*
----------------

.. warning::
    The docker approach is primarily a fallback for instances where you cannot
    (or will not) install Nix on the host system.

    You will miss certain benefits, such as launching your editor from within
    the environment and getting code-completion etc via LSP.

    It is, however, typically preferable to setting up Spex directly on the
    host system, as you are guaranteed to run Spex in the same environment as
    the developers tested the software in.

The Spex project also provides a way to build a dockerized version of the
Nix development environment.

To build the development environment container::

    make dev-docker-build

To enter into the development environment container::

    make dev-docker
