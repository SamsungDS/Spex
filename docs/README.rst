Documentation
=============

The ``spex`` documentation is written in Sphinx-Doc. Here is a brief overview:

* ``source``, here you will find the documentation sources, that is, the written text
* ``requirements.txt``, this is a list of Python packages needed to build the documentation
* ``Makefile``, this is helper, try typing 'make' and see what it tells you

Try typing this::

        make

This should install the requirements (``requirements.txt``) for building
the documentation and then print a ``help`` page, showing how to build
the documentation. A compound target is available, doing it **all**::

        make all
