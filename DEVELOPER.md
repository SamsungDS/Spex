# Developer Notes
Spex requires Python 3.11 and libxml2 which is used by the Python package, lxml, for
XML (docx) processing.

You may set up a proper development environment yourself, but for now, most Linux
distributions provide an older version of Python, making initial setup a little harder.

We therefore provide a reference environment via the Nix package manager. You can also
build and/or import a docker image which we create from the same Nix environment.

## Setting up the Nix environment

We would recommend following the instructions of the "Zero to Nix" guide
specificially the page on installing nix: https://zero-to-nix.com/start/install

**NOTE:** *if you install nix By other means,  be sure to enable flake support and the new CLI interface see [NixOS Wiki Entry on enabling flakes](https://nixos.wiki/wiki/Flakes#Enable_flakes)*.

### Getting started
This project provides a "Nix flake" which, broadly speaking, describes how to build
some software and how to configure a development environment. 

From within this directory, run `nix develop #.`, to enter a environment, which has
Python 3.11, libxml2 and all of the Spex python dependencies pre-installed.

From here, you may run spex using the command `python -m spex` (`python -m spex -h`
for hints on how to use Spex), and start making changes to the program.

## Docker

### Building the docker image
Building the docker image requires Nix, at which point you are better served by
simply using Nix. However, if you have Nix and wish to build the docker image,
simply run:

```
nix build .#dockerImage
```

However, you may ask a friend or colleague to build the image for you. If you
have the image, you simply need to import it to use it, see the section below.

### Using the docker image
The docker image is distributed as a tarball, to use it, you first import it like so:

```
docker load < image.tar.gz
```

Now you can run the Spex progam using the image. Something like the following
is necessary:
```
docker run --rm -it \
    --mount type=bind,source="$(pwd)",target="/out" \
    --mount type=bind,source="/home/jwd/NVM Express NVM Command Set Specification 1.0c.docx",target="/input.docx" \
    <the spex image> \
    spex -o /out /input.docx
```

Let's review:

* `docker run --rm -it` - is almost boiler-plate. We wish to run some new container, based of some image (to be specified later in the command). Also, we want to remove the container after use (`--rm`) and we want to run it interactively with a terminal `-it`.
* Docker spawns a container from the provided image, which provides a stand-alone Linux system. To access files from our host, we must map them into the container.
   * `--mount type=bind,source="$(pwd)",target="/out"` - maps the current directory into the container as `/out`
   * `--mount type=bind,source="/path/to/specification.docx",target="/input.docx"` - maps the provided document into the container as `/input.docx`
* `<the spex image>` - the docker image to use, after loading in the image, find it in the output of `docker ps`
* `spex -o /out /input.docx` - this is the actual spex command. Here, we parse `/input.docx`, placing all the output generated from this in `/out` (which we mapped to the current directory of the host). see `spex -h` for more information.