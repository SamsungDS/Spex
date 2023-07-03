#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. "${DIR}/_common.sh"

set -ex

flake8 spex --extend-ignore=E203,F401,F811,E501
mypy spex

black spex --check
isort spex --profile=black --check
