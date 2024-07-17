#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. "${DIR}/_common.sh"

set -ex

for file in ./dist/nvme_*.tar.gz ; do
    if [ -e "$file" ] ; then
        pipx install -v --include-deps --force "$file[dev]"
        pipx install -v --include-deps "$file[spexsrv]"
    fi
done

