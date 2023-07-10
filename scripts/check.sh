#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. "${DIR}/_common.sh"

set -ex

flake8 src/spex --extend-ignore=E203,F401,F811,E501
mypy src/spex

black src/spex --check
isort src/spex --profile=black --check
