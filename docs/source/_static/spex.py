#!/usr/bin/env python

# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

import sys
import argparse
from pathlib import Path
from contextlib import contextmanager
import os
import subprocess as sp


@contextmanager
def cwd(path: Path):
    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


def call(*args, **kwargs) -> sp.CompletedProcess:
    _fixed_args = {
        "shell": False,
        "check": True,
    }
    forbidden_keys = set(kwargs.keys()).intersection(set(_fixed_args.keys()))
    if forbidden_keys:
        raise RuntimeError(
            f"cannot override any of the args: {', '.join(forbidden_keys)}"
        )
    return sp.run(args, shell=False, check=True)


parser = argparse.ArgumentParser(description="run spex using docker", add_help=False)


SPEX_DOCKER_DIR = Path(__file__).parent
SPEX_ROOT = SPEX_DOCKER_DIR.parent
SPEX_IMG_NAME = "ghcr.io/openmpdk/spex"


parser.add_argument("--tag", default="main")
parser.add_argument("-h", "--help", action="store_true")


def cmd_run(args: argparse.Namespace, run_args: list[str]):
    vol_map = {}

    img = f"{SPEX_IMG_NAME}:{args.tag}"

    if args.help:
        call("docker", "run", "--rm", "-it", img, "spex", "-h")
        return

    def map_fn(arg):
        pa = Path(arg)
        if not pa.exists():
            return arg
        dst = str(Path("/volumes") / (pa.relative_to("/") if pa.absolute() else pa))
        vol_map[arg] = dst
        return dst

    spex_cli_args = [map_fn(arg) for arg in run_args]
    spex_args = [
        "docker",
        "run",
        "--rm",
        "-it",
        "--mount",
        f"type=bind,source={os.getcwd()},target=/host-cwd",
        "--workdir",
        "/host-cwd",
    ]

    for src, dst in vol_map.items():
        spex_args.extend(["--mount", f"type=bind,source={src},target={dst}"])

    spex_args.extend([img, "spex"])
    spex_args.extend(spex_cli_args)

    try:
        call(*spex_args)
    except sp.CalledProcessError as e:
        sys.exit(1)


def main():
    args, run_args = parser.parse_known_args()
    if args.help:
        print("!! NOTE: Spex running via docker")
        print()
        print("The Spex command-line options are described below, but you also")
        print("must decide which version of Spex to use.")
        print()
        print("1) Visit https://github.com/OpenMPDK/Spex/pkgs/container/spex/versions")
        print(
            "2) Next to each release will be a series of tags such as 'v1.0' or '700ae3c'."
        )
        print("   Select one corresponding to the version of Spex you wish to run.")
        print("")
        print(f"USAGE: {Path(__file__).name} --tag=v1.0 [SPEX command-line arguments]")

        print("\n\n")
        print("Spex command help:")

        img = f"{SPEX_IMG_NAME}:{args.tag}"
        call("docker", "run", "--rm", "-it", img, "spex", "-h")
        return

    cmd_run(args, run_args)
    # parser.print_help(sys.stderr)


if __name__ == "__main__":
    main()
