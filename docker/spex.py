#!/usr/bin/env python
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
        raise RuntimeError(f"cannot override any of the args: {', '.join(forbidden_keys)}")
    return sp.run(args, shell=False, check=True)


parser = argparse.ArgumentParser(
    description="build Spex docker image",
)


SPEX_DOCKER_DIR = Path(__file__).parent
SPEX_ROOT = SPEX_DOCKER_DIR.parent


cmd = parser.add_subparsers(dest="cmd")
build = cmd.add_parser("build")
build.add_argument("--skip-load", action="store_true", default=False)
clean = cmd.add_parser("build-clean")
run = cmd.add_parser("run", add_help=False)
run.add_argument("--image", required=True)
run.add_argument("-h", "--help", action="store_true")
run.add_argument("rest", nargs=argparse.REMAINDER)



def cmd_build(args: argparse.Namespace):
    with cwd(SPEX_ROOT):
        call("docker", "build", "-t", "spex-builder:latest", str(SPEX_DOCKER_DIR.absolute()))
        spex_root_str = str(SPEX_ROOT.absolute())
        call("docker", "run", "--rm", "-it",
             "--mount", "type=volume,source=spex-builder-store,target=/nix/store",
             "--mount", "type=volume,source=spex-builder-db,target=/nix/var/nix/db",
             "--mount", f"type=bind,source={spex_root_str},target=/spex-dir",
             "spex-builder:latest")

    print("")
    print("Build completed, the output image is saved to 'spex-docker.image.tar.gz'")
    print("")
    
    if args.skip_load:
        return
    
    print("Loading image into docker daemon...")
    with cwd(SPEX_ROOT):
        img = str((SPEX_ROOT / "spex-docker.image.tar.gz").absolute())
        call("docker", "load", "-i", img)
    


def cmd_clean():
    with cwd(SPEX_ROOT):
        for vol_suffix in {"db", "store"}:
            vol = f"spex-builder-{vol_suffix}"
            print(f"removing volume {vol}...")
            try:
                call("docker", "volume", "rm", vol)
            except sp.CalledProcessError as e:
                pass


def cmd_run(args: argparse.Namespace):
    run_args = args.rest
    vol_map = {}

    if args.help:
        call("docker", "run", "--rm", "-it", args.image, "spex", "-h")
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
        "docker", "run", "--rm", "-it",
        "--mount", f"type=bind,source={os.getcwd()},target=/host-cwd",
        "--workdir", "/host-cwd"
    ]

    for src, dst in vol_map.items():
        spex_args.extend(["--mount", f"type=bind,source={src},target={dst}"])


    spex_args.extend([args.image, "spex"])
    spex_args.extend(spex_cli_args)
    
    try:
        call(*spex_args)
    except sp.CalledProcessError as e:
        sys.exit(1)


def main():
    args = parser.parse_args()
    cmd = args.cmd
    
    if cmd == "build":
        cmd_build(args)
    elif cmd == "build-clean":
        cmd_clean()
    elif cmd == "run":
        cmd_run(args)
    else:
        parser.print_help(sys.stderr)


if __name__ == "__main__":
    main()
