# Spex

## Usage

```
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install /path/to/spex-repo
(venv) $ spex /path/to/specification-docx-or-html
```

During processing, spex will generate a HTML model (provided the file
passed as input is a .docx file), an accompanying CSS file (again, provided
parsing a .docx file) and a JSON file representing all the data-structures
which could be extracted from the specification.

The JSON file is called the "NVMe model" and contains two types of figures:
* struct table
* value table

Struct tables map to C structs, while value tables map to C enums.
Note that the model is flattened, nested tables are hoisted out to the top-level
and defined before the tables which use them.


By default, the generated output files are stored in the current working
directory. Use `-o /path/to/dir` to specify a different directory for the
generated files.


Producing the NVMe model involves a lot of processing of the raw table figures.
In doing so, multiple linting errors will be raised, indicating potential or
active issues with the source material.
You can ignore some classes of errors by adding `--lint-ignore=...` to the
command. See `spex --help` for details.

## Example - From Spec. to Code

Place your ``.docx`` specification documents in the ``input`` folder then run:

```
make magic
```

The above will do "magic" in the form of:

* Extract tables and figures from ``.docx`` into a ``.html`` file
* Convert the ``.html`` to ``.json`` format -- normalized and cleaned up
* Convert the ``.json`` to **yace** ``.yaml``
* Produce C API  using the **yace** ``.yaml``

Note: this requires a version of **yace** which have not yet been released.

Have a look at the intermediate files produced in ``builddir`` and the API in
``output``.

## Background

During processing, spex will generate a HTML model (provided the file passed as
input is a .docx file), an accompanying CSS file (again, provided parsing a
.docx file) and a JSON file representing all the data-structures which could be
extracted from the specification.

The JSON file is called the "NVMe model" and contains two types of figures:

* struct table
* value table

Struct tables map to C structs, while value tables map to C enums. Note that
the model is flattened, nested tables are hoisted out to the top-level and
defined before the tables which use them.

By default, the generated output files are stored in the current working
directory. Use `-o /path/to/dir` to specify a different directory for the
generated files.

Producing the NVMe model involves a lot of processing of the raw table figures.
In doing so, multiple linting errors will be raised, indicating potential or
active issues with the source material. You can ignore some classes of errors
by adding `--lint-ignore=...` to the command. See `spex --help` for details.
