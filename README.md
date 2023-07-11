<!--
SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd

SPDX-License-Identifier: BSD-3-Clause
-->

# Spex

## What is Spex?
Spex is a tool for linting- and generating a structured representation
of the data-structures contained in an NVMe specification document.

Please see the full documentation at: https://openmpdk.github.io/Spex


## For users
### Installing/Using Spex
#### Using Nix (Recommended)
Given a copy of Nix, the environment will be automatically configured, and is
guaranteed to match the environment in which we develop and for which CI testing
is done.

See https://openmpdk.github.io/Spex/setup/nix.html for details.

**NOTE** Nix works natively on Linux and MacOS, and on Windows via WSL. See the
link above for notes on installing- and using Nix on all 3 platforms.


#### Directly on your machine (Discouraged)

`make install` installs **Spex** *for your user* in a separate Python virtual
environment - meaning the dependencies of **Spex** are not impacted by other Python
software you install.
`make uninstall` removes **Spex**, if installed.

Accomplishing this sadly requires a third-party tool, `pipx`, which we however
*highly recommend*. Please see the [pipx site](https://pypa.github.io/pipx/)
for notes on installing this tool.

**NOTE** that in this case, you will still need Python 3.11 or later *and*
`libxml2`.

### Using Spex

See https://openmpdk.github.io/Spex/user_guide/using_spex.html for
details.

## For developers

### Setting up the development environment
Note that targets like `build`, `check`, `format` and `docs` all expect to operate
in a properly configured environment.

*We strongly recommend using Nix directly*. It takes care of everything and
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
These targets respectively build and removes a source distribution python package.
You most likely won't need or want this.
