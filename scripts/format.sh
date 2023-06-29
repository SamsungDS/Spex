#!/usr/bin/env bash
on_err() {
    set +x
    if [ ! -n "$SPEX_NIX_ENV" ]; then
        echo "WARN> script not running in Nix development environment."
    fi
}
trap 'on_err' ERR


set -ex

black spex
isort --profile=black spex 
