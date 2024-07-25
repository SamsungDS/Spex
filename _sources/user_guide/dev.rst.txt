.. _sec-guide-dev:

Development Guide
=================

The following are some quick notes to help you get started with the **Spex** codebase.

Overview
--------

1. Extract table-like figures and document metadata - create stage 1 document
2. Using document metadata, select appropriate **DocumentParser**
3. Use **DocumentParser** to iterate over all figures
4. For each figure: extract its contents (fields/values) using an **Extractor**.
5. save to stage 2 document

Terminology
-----------
**DocumentParser**
    A class responsible for driving the parsing of a document. It defines a method to iterate
    over figures, defines a list of default **Extractors** to try when extracting the contents
    of a figure and allows explicitly overriding/defining a specific extractor to use for a figure.
    Finally, a **DocumentParser** also allows you to override the label (field name) and brief
    (one-line description) of any field of any figure - as a way to enhance or improve the
    generated output.

**Extractor**
    An extractor is responsible for *extracting* the raw contents of a figure (a HTML table),
    making sense of it (i.e. identifying field names, ranges etc) and transforming it into
    one of the standard **entity** types which **Spex** operates with, namely **value** and
    **struct**.

**Entity**
    The stage 2 document (JSON) will contain a list of entities, each corresponding either
    to a top-level figure, or some figure found nested within another figure.
    An entity can presently be of two types, **value**, which describes something typically
    rendered in C as an enum, or a (bit|byte) **struct**. A struct entities have one or more
    fields with clearly defined ordering and sizes, as defined by their ranges. A struct with
    bit ranges could be represented as a bit field in C, or as an array of values with macros
    to extract each "field". A struct with byte ranges cleanly maps to a packed struct in C.

**Stage 0/1/2 Document**
    See :ref:`sec-guide-stages`.

**Quirks**
    Ideally all figures across all documents should be possible to parse using the same set of
    standard extractors. We expect to work toward this in the future, but for now, we may need
    to implement custom processing for specific figures. To do this, we create a custom
    **DocumentParser** class and define overrides for specific figures within the document.
    We then install this **DocumentParser**, containing the relevant overrides, into the
    central **quirks map**, where **Spex** looks for a **DocumentParser** based on the
    ``(title, revision)`` key extracted from the document's page header.

(Detailed) Overview
-------------------

1. Create stage 1 document
~~~~~~~~~~~~~~~~~~~~~~~~~~
This stage is skipped if the input document is already a stage 1 document (HTML).

Otherwise, the original full specification is opened and all table-like figures
are extracted from the docx file and their form is translated into HTML and stored
into a stage 1 document.

Additionally, the document title and revision, visible on the page header on each
page, is extracted and embedded into the document. **Spex** uses this to uniquely
identify the document - and this allows us to define a custom **DocumentParser**
for the document, if need be.

2. Select appropriate **DocumentParser**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Spex** determines the correct **DocumentParser** to use by forming a unique
key from the document title and revision, and looking up in a "quirks"
dictionary.
The quirks dictionary is defined in ``spex/jsonspec/quirks/__init__.py``.
Specialized document parsers are defined under ``spex/jsonspec/quirks``.

Otherwise, the default **DocumentParser** is used. Note that a specific
**DocumentParser** is only necessary provided we need to override which
extractor is applied to one or more figures, manually provide labels for
one or more fields or otherwise override parsing.

3. Iterate over all figures
~~~~~~~~~~~~~~~~~~~~~~~~~~~
The **DocumentParser** class (``spex/jsonspec/document.py``) provides the 
``DocumentParser.parse`` method, which iterates over all top-level figures
in order, calling ``DocumentParser._on_parse_fig()`` on each figure found.

The ``_on_parse_fig()`` method then finds an appropriate **Extractor** to
apply (see below) which, among other things, may encounter additional
*nested* figures.
It is the responsibility of the **Extractor** to invoke a callback
(which points to ``DocumentParser._on_parse_fig()``) for each nested
figure it encounters.
This allows a **Extractor** to facilitate recursively parsing all relevant
nested figures, while ignoring irrelevant tables in other columns, for instance.

4. Apply an appropriate **Extractor** to extract figure contents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For each figure encountered, ``DocumentParser._on_parse_fig()`` is called.
This method first finds a suitable **Extractor** to use (or errors out), then
it applies it, getting a generator of **Entities**, it yields to its caller in turn.

Finding the **Extractor** to use
""""""""""""""""""""""""""""""""
The process to determine the **Extractor** to use is the following:

First look in ``DocumentParser.fig_extractor_overrides`` for an entry
matching the key of the ID of this figure.
This option is only used in case a the figure requires special processing.
In that case, we may provide a special extractor, usually a specialization
of the bits, bytes or value extractor, to handle processing.
These are typically defined alongside the specialized **DocumentExtrator**
in the ``spex/jsonspec/extractors/quirks`` package.

.. note::
    **How are figures assigned an ID?**
    For top-level figures, the ID is the number of the figure itself. For
    nested figures, the **Extractor** used should construct a unique ID from
    the parent ID and some unique data from the row, typically the bit/byte
    offset or value from a value table.


In most cases, there is no specific override for a figure, and so the default
extractors, as specified by ``DocumentParser.extractors`` are tried, in order.
These are presently ``BytesTableExtractor``, ``ValueTableExtractor`` and
``BitsTableExtractor``, all defined in ``spex/jsonspec/extractors``.

In case of these extractors, the method tries each in turn, calling
the ``Extractor.can_apply()`` method on each, providing the extractor the
columns of the table. It is from the column names alone that an
extractor decides whether it is applicable or not.


