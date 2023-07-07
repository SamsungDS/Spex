# Spex

## What is Spex?
Spex is a tool for linting- and generating a structured representation
of the data-structures contained in an NVMe specification document.

Please see the full documentation at: https://openmpdk.github.io/Spex


## For users
### Installing/Using Spex
#### Recommended: Using Nix
Given a copy of Nix, the environment will be automatically configured, and is
guaranteed to match the environment in which we develop and for which CI testing
is done.

See https://openmpdk.github.io/Spex/setup/nix.html for details.

**NOTE** Nix works natively on Linux and MacOS, and on Windows via WSL. See the
link above for notes on installing- and using Nix on all 3 platforms.


#### Directly on your machine: `install` | `uninstall`

`make install` installs **Spex** *for your user* in a separate Python virtual
environment - meaning the dependencies of **Spex** are not impacted by other Python
software you install.
`make uninstall` removes **Spex**, if installed.

Accomplishing this sadly requires a third-party tool, `pipx`, which we however
*highly recommend*. Please see the [pipx site](https://pypa.github.io/pipx/)
for notes on installing this tool.

**NOTE** that in this case, you will still need Python 3.11 or later *and*
`libxml2`.

## For developers

### Setting up the development environment
Note that targets like `build`, `check`, `format` and `docs` all expect to operate
in a properly configured environment.

We *strongly* recommend using Nix directly. It takes care of everything and
ensures that editors can leverage the environment for code-completion and
navigation.
See https://openmpdk.github.io/Spex/setup/nix.html

To understand your options, see https://openmpdk.github.io/Spex/setup/index.html

Finally, if you use nix, `make dev` will put you inside a properly configured
development environment. `make dev-docker-build dev-docker` will do the same, but
within a container.

### `make check`
This target runs *all* the tests that our regular CI run would to ensure the software
is in a good state. If you make modifications, please run this before submitting.

### `make format`
This target automatically re-arranges package imports and reformats the code
to comply with our coding standards. Please use this ahead of submitting changes.

### `make docs`
This target builds the documentation locally. This is mostly useful when writing
previewing changes to the documentation locally.

### `build` | `clean`
These targets respectively builds- and removes a source distribution python package.
You most likely won't need or want this.





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
