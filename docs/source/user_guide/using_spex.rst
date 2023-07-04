.. _sec-using-spex:

Using Spex
==========

.. warning::
    **What are stages?**

    This section will frequently mention documents by the stage they are
    produced. See :ref:`sec-guide-stages` to read more.


**Spex** can take one or more stage 0 or stage 1 documents and produce for
each a stage 2 document, which describes the data-structures found in a
format convenient for further processing.
See the :ref:`introduction <sec-what-is-spex>` for more information.


Getting help
------------

Running ``spex`` without any arguments displays a summary of the command-line
interface.

At the time of writing, the usage string is the following::

    spex [-h] [-s] [-o OUTPUT] [--lint-ignore LINT_IGNORE] input [input ...]

This implies that the flags ``-s``  and ``-h``
take no arguments, while ``-o`` and ``--lint-ignore`` takes *exactly
one* argument each. Finally, all flags are surrounded by ``[  ]``, meaning they
are *optional*.

The command must also take *at least* one input document, but arbitrarily many
more documents (``[input ...]``) may be provided.

Parameters
----------

``-s`` / ``--skip-figure-on-error``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When **Spex** processes a document, each figure found is processed in order
of appearance. If **Spex** fails to process a figure, processing is aborted
(fail fast).

You can provide this flag change that, causing **Spex** to skip any figure
it cannot process rather than aborting processing outright.
This will produce faulty stage 2 documents, but is useful when developing
Spex or updating/authoring a new specification document where you want to
determine how many/which figures **Spex** has trouble processing.

``-o`` / ``--output``
~~~~~~~~~~~~~~~~~~~~~
By default, **Spex** writes the stage 2 document and any error log to the
current directory. This flag can be provided to cause the document(s) to
be written elsewhere.

``--lint-ignore``
~~~~~~~~~~~~~~~~~
When processing a document, Spex will complain if something is problematic/wrong.
The causes of this are generally one of:

1. Something is incorrectly specified
    * (e.g. a range where the start- and end- ranges are reversed)
    * (e.g. overlapping fields in some data-structure)
2. Information is missing
    * (e.g. a field in some data-structure is missing a name - **Spex** must invent one)


In some cases, you may wish to ignore certain classes of errors to reduce the
amount of output and allow you to focus on specific types of errors.

In this case, you can add something like ``--lint-ignore T1001,R1002`` to
ignore all instances of those lint codes.

To see a complete list of lint codes, run ``spex`` (without arguments) or
``spex -h``.
