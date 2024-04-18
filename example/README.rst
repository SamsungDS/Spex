  SPDX-FileCopyrightText: 2024 Samsung Electronics Co., Ltd

  SPDX-License-Identifier: BSD-3-Clause


Workflow Example
================

This is a an example of using the spex command-line tool. The example is split
in two, one for NVMe workgroup members and one for the public. The reason being
that NVMe workgroup members has access to **stage0** (DOCX) specification
documents, the public does not.

For NVMe members
----------------

Place the **stage0** (DOCX) documents in the ``stage0/`` folder, and then run::

  spex stage0/*.docx --skip-figure-on-error --output output/

When doing so, ``spex`` will convert the **stage0** documents and store
**stage1** and **stage2** versions of the files in the ``output`` folder.

For public
----------

In the repository, at ``example/stage1``, specification documents are provided
in **stage1** (HTML) format.

  spex stage1/*.html --skip-figure-on-error --output stage2/

Consult the directory ``stage2`` to see the **stage2** specification documents.

.. note::
   See ``spex.log`` for any issues arrising when running the above.
