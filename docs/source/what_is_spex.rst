.. _sec-what-is-spex:

What is Spex?
=============

Spex is a tool for validating and extracting a structured output
representing the figures describing data-structures in NVMe
specification documents.

Broadly speaking, Spex aims to solve two problems:

1. Aid the NVMe specification document authors in finding errors and inconsistencies in data-structures ahead of release
2. Give downstream projects a new artifact describing all data-structures which is well-defined and easy to parse programmatically
    * This makes it easy for projects to write code-generators


How Spex improves the state of affairs
--------------------------------------
Prior to Spex, the `nvme-lint <https://nvmexpress.org/nvme-lint-new-open-source-tool-to-help-validate-the-nvm-express-specifications/>`_ tool was introduced
to solve the first issue. Prior to nvme-lint, validation was entirely manual which has
occasionally led to issues in the NVMe data-structures.

Additionally,  downstream projects would previously have to translate specifications to
code manually, and to manually update these artifacts as the specifications
themselves evolved. With the introduction of Spex, it becomes easy to track changes
by comparing the models of two revisions of the same specification, or write a code-generator
which uses the model to generate the code describing the data-structures.

How Spex aids in validation
---------------------------
Spex handles validation like nvme-lint would, but parses the NVMe specification documents
in their original docx (Microsoft Open Document format) form rather than PDF. These
documents are internal to the working group, but provide a more reliable result than PDF.

As Spex parses a document, any issues encountered during parsing is recorded as a linting
issue in the produced document.
Spex will detect improperly specified bit/byte ranges, holes between or overlapping fields
and much more.

Producing a model for downstream consumption
--------------------------------------------
The output of Spex parsing either a docx or html file, is a structured
JSON document, describing the data-structures (entities) found within the
document. These entities come in two types: value entitites which are
typically represented as ``enum`` definitions in C, and ``bits`` or ``bytes``
entities which typically are represented as ``struct`` definitions in C.

This JSON output conforms to the JSON schema ``nvme-model.schema.json``. In
addition to describing the data-structures of the specification, the file also
contains a ``lint`` section, which describes ambiguities and errors in
the specification, and instances where spex was unable to parse a data-structure.
The purpose of these ``lint`` entries is to aid the specification writers in
catching issues such as overlapping fields, invalid field range specifications,
duplicate field names and so on.


Why does Spex not generate C code or bindings directly?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
While generating code for the various data-structures described by the specification
is a motivating factor for writing Spex, we have deliberately left it out.
Firstly, not all downstream projects use C, secondly, each C project have different
formatting expectations, macros and ideas of which C features to use.

Spex extracts structured, well-defined descriptions of the data-structures contained
in each specification document, it is up to you to merge these descriptions where
appropriate and to write a tool for generating code suitable to your project.