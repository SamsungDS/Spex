.. _sec-what-is-spex:

What is Spex?
=============

The Specification Extraction Tool aka **Spex**, is a command-line tool that
does two things:

1. Checks the integrity of a given :nvme:`NVMe <>` specification document in
   ``.docx`` format

2. Extracts figures from a given :nvme:`NVMe <>` specification document in
   ``.docx`` and stores the figures in formats which are more convenient to
   work with programmatically

   * :html:`HTML <>`: This is useful for human as well as machine
     interpretation.
   
   * :json:`JSON <>`: The :json:`JSON <>` format utilized is verifiable
     by a :json-schema:`JSON-Schema <>`. This format is primarily
     intended for programmatic consumption, for examply by
     code-generators.

**Spex** provides the above functionality as it aims to:

* Aid the :nvme:`NVMe <>` specification document authors in finding errors and
  inconsistencies in data-structures ahead of release

* Give downstream projects a new **artifact** describing all data-structures
  which is well-defined and easy to parse programmatically

Here we refer to **downstream** as the adopters of :nvme:`NVMe <>` in
open-source projects.

How Spex improves the state of affairs
--------------------------------------

Prior to **Spex**, the :nvme-lint:`nvme-lint <>` tool (see
:nvme-lint-post:`nvme-lint post <>`) was introduced to solve the first task
(checking the spec. documents). Prior to :nvme-lint:`nvme-lint <>`, validation
was entirely manual which has occasionally led to issues in the :nvme:`NVMe <>`
data-structures.

Additionally, downstream projects would previously have to translate
specifications to code manually, and to manually update these artifacts as the
specifications themselves evolved.

With the introduction of **Spex**, it becomes easy to track changes by
comparing the :json:`JSON <>` document of two revisions of the same
specification, or write a code-generator which uses the :json:`JSON <>`
document(s) to generate the code describing the data-structures.

Document Validation for specification authors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Spex** handles validation like :nvme-lint:`nvme-lint <>` would. However,
:nvme-lint:`nvme-lint <>` uses the publicly available ``.pdf`` documents as
input where **Spex** uses ``.docx`` (Microsoft Open Document format).

This is because **Spex** is intended to be used by the specification authors
before publishing the finalized specification documents. To name a few, then
**Spex** currently catches the following integrity issues:

* Improperly specified bit/byte ranges
* Holes between or overlapping fields
* Invalidly named figures

**TODO: Where is the list of things? This is something we should be able to extract from code using autodoc.**

HTML as intermediate representation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**TODO: describe what this is provided.**

Structured JSON for downstream consumption
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :json:`JSON <>` document produced by **Spex** is a structured document.
That is, the content is verifiable using a :json-schema:`JSON-Schema <>`, see
:repos-blob:`stage2.schema.json <src/spex/resources/stage2.schema.json>` . The
content represents two things:

* The Figures with table-like data which in the specification document
  describes data layout of among other things commands and command-results, and
  the description of values e.g. command opcodes, command completion status
  codes etc.

* A ``lint`` section, listing issues found in the specification document

The ``lint`` section describes ambiguities and errors in the specification
document, and instances where spex was unable to parse a figure in the
specification document. The purpose of these ``lint`` entries is to aid the
specification writers in catching issues such as overlapping fields, invalid
field range specifications, duplicate field names and so on.

What is it not?
---------------

To clarify the scope of **Spex** then this describes what **Spex** is not. For
example, **Spex** is *not* a code-generator and **Spex** does *not* provide a
semantically rich model of the entire :nvme:`NVMe <>` specification.

Why does Spex *not* generate C code or bindings directly?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While generating code for the various data-structures described by the
specification is a motivating factor for writing **Spex**, we have deliberately
left it out. Firstly, not all downstream projects use C, secondly, each C
project have different formatting expectations, macros and ideas of which C
features to use.

**Spex** extracts structured, well-defined descriptions of the data-structures
contained in each specification document, it is up to you to merge these
descriptions where appropriate and to write a tool for generating code suitable
to your project.

Why does Spex *not* produce an NVMe Model?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

...
