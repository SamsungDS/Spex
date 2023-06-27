.. _sec-what-is-spex:

What is Spex?
=============

Spex is a tool for analyzing and extracting a structured output
representing the figures describing data-structures in NVMe
specification documents.

Spex can parse the internally circulated Word (docx) specifications
in full or the publicly released HTML documents which are an extract
of all the figures describing data-structures.

The output of Spex parsing either a docx or html file, is a structured
JSON document, describing the data-structures (entities) found within the
document. These entities come in two types: value entitites which are
typically represented as ``enum`` definitions in C, and ``bits`` or ``bytes``
entities which typically are represented as ``struct`` definitions in C.

This JSON output conforms to the JSON schema `nvme-model.schema.json`. In
addition to describing the data-structures of the specification, the file also
contains a ``lint`` section, which describes ambiguities and errors in
the specification, and instances where spex was unable to parse a data-structure.
The purpose of these ``lint`` entries is to aid the specification writers in
catching issues such as overlapping fields, invalid field range specifications,
duplicate field names and so on.

Additionally, Spex provides benefits to the downstream consumers of NVMe
specifications. Firstly by acting as an additional validation tool to
prevent errors, secondly by providing structured, well-defined output
amenable to programmatic parsing and therefore code-generation.

Previously, downstream projects would have to translate specifications to
code manually, and to manually update these artifacts as the specifications
themselves evolved. With the introduction of Spex, writing tool to generate
this code becomes significantly easier.
