#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. "${DIR}/_common.sh"

set -ex

cd "${SPEX_ROOT}/docs"
BUILDDIR="${SPEX_ROOT}/docs/build" make html
BUILDDIR="${SPEX_ROOT}/docs/build" make linkcheck