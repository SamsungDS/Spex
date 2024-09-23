#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause


app_name=$(basename $0)
  
sub_help(){
    echo "Usage: $app_name <subcommand> [options]\n"
    echo "Subcommands:"
    echo "    webserver   Start webserver for linting NVMe specifications"
    echo "    run         Run NVMe-Spex"
    echo ""
}

  
subcommand="${1}"
case $subcommand in
    "" | "-h" | "--help")
        sub_help
        ;;
    "run")
        shift
        echo "Running nvme-spex ${@}"
        spex $@
        exit 0
        ;;
    "webserver")
        echo "Webserver starting"
        hypercorn --reload --bind 0.0.0.0:8000 spexsrv.application.app:app
        exit 0
        ;;
    *)
        echo "Error: '$subcommand' is not a known subcommand." >&2
        echo "       Run '$app_name --help' for a list of known subcommands." >&2
        exit 1
        ;;
esac