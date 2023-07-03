#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. "${DIR}/_common.sh"

set -ex

cd "${SPEX_ROOT}/docs"
BUILDDIR="${SPEX_ROOT}/docs/build" make html
BUILDDIR="${SPEX_ROOT}/docs/build" make linkcheck