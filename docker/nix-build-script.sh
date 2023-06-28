#!/usr/bin/env bash

# Executed inside the Nix container.
# This script just triggers the build of the docker image output,
# then copies the resulting file (a compressed docker image) out
# of the Nix store and into the current directory.
set -ex
nix build .#dockerImage
cp result ./spex-docker.image.tar.gz
