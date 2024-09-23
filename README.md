<!--
SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd

SPDX-License-Identifier: BSD-3-Clause
-->

# NVMe-Spex
[![Build status](https://github.com/SamsungDS/Spex/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/SamsungDS/Spex/actions/workflows/build-docs.yml)
[![python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## What is NVMe-Spex?
NVMe-Spex is a tool for linting- and generating a structured representation of the
data-structures contained in an NVMe specification
document(https://nvmexpress.org/).

NVMe-Spex provides two front-ends to interact with the tool. The most basic
interface to interact with NVMe-Spex is the command line tool as an alternative
a web-application is also provided where the docx/html files can be uploaded and
processed.

Please see the full documentation at: https://samsungds.github.io/Spex/

## Installing NVMe-Spex
There are multiple options for installing NVME-Spex. The list of supported
method is: **Nix** package, **python** package, **docker** image and installing
nvme-spex from source.

### Dependencies
NVME-Spex has libxml2(https://gitlab.gnome.org/GNOME/libxml2) as a dependency.
In any other case than for Nix and docker installs it is necessary to install
libxml2 manually.

#### `Apt based Linux`
For apt based systems such as debian or ubuntu the following commands will
install libxml2:

```
sudo apt update

sudo apt install libxml2-dev
```

#### `OSX`

Open a terminal and issue the following command to install libxml2:

```
brew install libxml2
```

### Installing with Nix

Given a copy of Nix, the environment will be automatically configured, and is
guaranteed to match the environment in which we develop and for which CI testing
is done.

See https://samsungds.github.io/Spex/setup/nix.html for details.

**NOTE** Nix works natively on Linux and MacOS, and on Windows via WSL. See the
link above for notes on installing- and using Nix on all 3 platforms.

### Installing with pipx
It is possible to install the nvme-spex tool directly from pypi.org via the pipx or
pip tool. The nvme-spex tool is build with lxml and therefor has a none python
dependency that needs to be installed which is **libxml2**. See instructions for
you particular operation systems to install libxml2. 

When the dependency is met is is possible to install nvme-spex with following
command:

```
pipx install nvme-spex
```

**NOTE** that in this case, you will still need Python 3.11 or later *and*
`libxml2`.

### Installing webserver with docker

NVMe-Spex is also packaged as a docker container image and can the newest
release can be pulled and run by executing the following docker commands:

```
docker pull ghcr.io/samsungds/nvme-spex-webserver:latest

docker run -p 8000:8000 ghcr.io/samsungds/nvme-spex-webserver:latest
```

When the docker container is successfully running the web application can be
accessed in the browser at http://localhost:8000 .

**Note** for Windows it is possible to install docker though the docker
desktop(https://docs.docker.com/desktop/install/windows-install/) or the podman
project (https://podman.io/docs/installation). We aware of docker desktops
licensing model.

### Installing from source

Clone repository with git:

```
git clone git@github.com:SamsungDS/Spex.git

cd spex

make build install
```

`make build install` build the package and installs **Spex** *for your user* in
a separate Python virtual environment - meaning the dependencies of **Spex** are
not impacted by other Python software you install.  `make uninstall` removes
**Spex**, if installed.

**NOTE** that in this case, you will still need Python 3.11 or later *and*
`libxml2`.

## Using Spex

See https://openmpdk.github.io/Spex/user_guide/using_spex.html for details.


## Setting up the development environment

Note that targets like `build`, `check`, `format` and `docs` all expect to
operate in a properly configured environment.

To understand your options, see https://samsungds.github.io/Spex/setup/index.html

Finally, if you use nix, `make dev` will put you inside a properly configured
development environment.

### `make check`
This target runs *all* the tests that our regular CI run would to ensure the
software is in a good state. If you make modifications, please run this before
submitting.

### `make format`
This target automatically re-arranges package imports and reformats the code to
comply with our coding standards. Please use this ahead of submitting changes.

### `make docs`
This target builds the documentation locally. This is mostly useful when writing
previewing changes to the documentation locally.

### `make build` | `clean`
These targets respectively build and removes a source distribution python
package.  You most likely won't need or want this.
