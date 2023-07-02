.. _sec-guide-stages:

Stages
======

Spex is deliberately designed to break processing into a series of
discrete and individually verifiable stages.

Stage artifacts
~~~~~~~~~~~~~~~

Each stage generate one or more files as its output. These files are referred
to by their stage elsewhere in documentation. Each stage's output is presently
a file of a different file type, but this may change in the future, as possibly
additional steps of processing are added. Thus it is better to refer to a
document by its stage than file type.

* **Stage 0** - the NVMe specification document (in docx)
* **Stage 1** - the HTML file containing an extract of all table-like figures from stage 0.
* **Stage 2** - the JSON document representing all data-structures found in the document. These are either enum-like pairs of names and assigned codes/values, or struct-like data-structures, where each field is decribed by its range and field name.

Why organize the program into stages?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Breaking the program into distinct stages is beneficial to development and
testing/verifying the output produced. However, it also has an important benefit to
users: the ability to opt-out at any point of processing.

Each step of processing makes the output more predictable and easy to process, but
it also throws away information. For example, in processing the docx document to
HTML, spex throws away every graphic and text between the tables.

In producing the stage 2 output, the data-structure model, Spex discards supplementary
text, figure headers, table section headers and so on.
Each stage further refines the data, but discards other data in the process.
