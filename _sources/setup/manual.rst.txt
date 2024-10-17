.. _sec-setup-manual:

Setting up Spex manually
========================

.. note::
    In doubt as to which method to use when setting up Spex? See :ref:`sec-setup`.


.. warning::
    Spex reserves the right to update dependencies if it
    helps development or enables new features or better performance.
    
    If you choose the manual route, it is up to *you* to update your system
    accordingly.

**Spex** is implemented in Python and distributed via :pypi:`Pypi <>` and thus
installable via ``pip`` / ``pipx``::

  pipx install nvme-spex

And then run it::

  spex --help

For this to run then the following runtime requirements must be met:

1. Python >= 3.11
    * **spex** relies on Python features for types introduced in Python 3.11

2. Python packages
    * For details, then have a look at the **Spex** flake (``setup.cfg``)

3. C libraries used by the Python packages
    * Specificaly, then **Spex** uses the Python package ``lxml`` which in turn
      requires the ``libxml2`` C library to be present on the system.
    * This may change and more dependencies may be added, see the ``flake.nix`` file for full details.


.. note::
    The setup of the above requirements is specific to the environment that you are
    using. The only supported environment is the reference environment, managed by
    :ref:`sec-setup-nix`
