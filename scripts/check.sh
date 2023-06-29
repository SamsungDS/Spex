#!/usr/bin/env bash

on_err() {
    set +x
    if [ ! -n "$SPEX_NIX_ENV" ]; then
        echo "WARN> script encountered an error during execution."
        echo ""
        echo "This script exited due to an error. However, this script was"
        echo "also run outside of the nix development environment."
        echo ""
        echo "In case of an abnormal/unexpected error - please check your environment."
    fi
}
trap 'on_err' ERR

set -ex

flake8 spex
mypy spex
