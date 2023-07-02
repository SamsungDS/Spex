.. _sec-setup-manual:

Setting up Spex manually
========================

If you are reasonably comfortable with Python virtual environments and
installing system libraries and alternative copies of Python, then manually
setting up Spex is just fine.

The benefit of this approach is needing neither Nix or Docker. But there is no
hand-holding with this approach. You will be required to infer the dependencies
needed from skimming the ``nix.flake`` and ``setup.cfg`` files, and to install
the required components.

This is likely to be a sufficiently recent copy of the Python interpreter, C
libraries such as ``libxml2`` and the Python packages listed in the above
files.

Please note that dependencies may change and the only full, canonical
specification of what is required is described in the ``nix.flake`` file.


.. warning::
    As mentioned above - Spex reserves the right to update dependencies if it
    helps development or enables new features or better performance.
    
    If you choose the manual route, it is up to *you* to update your system
    accordingly.


.. note::
    In doubt as to which method to use when setting up Spex? See :ref:`sec-setup`.


.. warning::
    Manually setting up Spex means *you* are responsible for installing the
    C libraries and Python packages that Spex needs, and that the version of
    Python used is recent enough.

    This page is a place-holder -- if you choose this option, you should know
    what to do. If you don't, use the Nix or Docker methods.
