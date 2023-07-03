.. _sec-using-spex:

Using Spex
==========

.. warning::
    This section will frequently mention documents by the stage they are
    produced. See :ref:`sec-guide-stages` to read more.

As mentioned in the :ref:`introduction <sec-what-is-spex>`, Spex parses one
or more input documents and produces for each a corresponding structured JSON
output document, describing the data-structures found in the document.

The input file can either be a NVMe specification document in docx format,
or an HTML file produced by extracting all figures in an NVMe specification
and rendering them in HTML.

.. note::
    The NVMe specification document (in .docx) is actually the stage 0
    document from which the stage 1 document, the HTML file, is produced.

    To read more about stages, see :ref:`sec-guide-stages`.

