.. _sec-setup-docker:

Setting up Spex using Docker
============================

.. note::
    In doubt as to which method to use when setting up Spex? See :ref:`sec-setup`.


.. warning::
    The docker approach is primarily a fallback for instances where you cannot
    install Nix on the host system.

    It is, however, typically preferable to setting up Spex directly on the
    host system, as you are guaranteed to run Spex in the same environment as
    the developers tested the software in.

Setup
-----

The docker setup process is a two-step process:

1. Build a docker image for spex using a script provided in this repository
2. Import/load the docker image into your Docker instance

Build docker image
~~~~~~~~~~~~~~~~~~

.. warning::
    Remember that you must rebuild the image when updating Spex.
    This is because both Spex and the entire Nix environment is embedded inside
    the image.


To build the docker image stand in the root of the Spex project and run
the following command: ``python docker/spex.py build``.

.. note::
    **How is the image built? Why are we using a script?**

    If you are curious as to why there is a script - we actually use Nix to
    build the docker image itself on top of NixOS, this allows us to use the
    *exact* same environment as defined in Nix. However, this *requires* Nix.
    To work around this, we first build a build container from the upstream
    `nixos/nix` docker Image, into which we map the Spex source directory
    and use the ``dockerImage`` output of the Nix flake to build the actual
    image, which is then copied back out into the host.

Once done, you will have a new ``spex-docker-image.tar.gz`` file in the root
of the Spex directory. This is the finished docker image.
Unless you add ``--skip-load``, the image will also have been loaded into
the docker daemon, making it available for use.

In my case the newly built image was tagged ``20230621221410-dirty``,
because the git repository contained uncommitted changes at the time,
of building the image.

.. note::
    **Why are we loading in the docker image?**

    ``docker load`` copies the image data to where-ever
    the actual docker daemon is located (local or remote), and you
    may remove the image file afterwards to save space.


Use the image
-------------

To run Spex from within docker, you will need a command akin to this::

    python docker/spex.py run --image spex:20230621221410-dirty \
        -o /out "/home/jwd/NVM Express NVM Command Set Specification 1.0c.docx"

The first line are the arguments necessary to launch spex from within the
built docker image. Every other argument is passed on spex directly.

To explore the Spex command-line interface, pass the ``--help`` flag like so::

    python docker/spex.py run --image spex:20230621221410-dirty --help

.. note::
    **Why are we using a script to launch Spex using docker?**

    Docker spawns containers from images. These containers are self-contained
    systems with their own file systems.

    Spex, however, operates on input files from the host, and those must be
    mapped in to the container, this also applies to the current working
    directory, into which Spex will write its output files unless another
    output directory has been specified.
    Even so, in case of crashes, a ``spex.log`` file is written to the
    current directory, detailing what went wrong.

    Replicating this behavior with docker is possible, provided one mounts
    each input file, output directory and the current working directory,
    and takes care to set the current working directory of the container to
    that of the (mounted) host current working directory.

    The script ensures all of this is done correctly.
    