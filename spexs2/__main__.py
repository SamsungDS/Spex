import argparse
from pathlib import Path
import textwrap


def arg_input(arg: str) -> Path:
    p = Path(arg)
    if not p.exists():
        raise RuntimeError(f"no file at '{p}'")
    elif not p.is_file():
        raise RuntimeError(f"path '{p}' exists, but is not a file")
    return p


def arg_output(arg: str) -> Path:
    p = Path(arg)
    if p.is_dir():
        raise RuntimeError(f"output must be a directory (or omitted)")

    return p


def main():
    epilog = textwrap.dedent("""
    Notes:
    ~~~~~~
    * output:
      if `output` is a directory, a correspondingly named JSON file is
      created for every input given.
      If `output` is omitted, the JSON output is pretty-printed to stdout.
    """)
    parser = argparse.ArgumentParser(
        description="Extract data-structures from HTML spec",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input", nargs="+", type=arg_input,
        help="One or more specification HTML files to extract data-structures from"
    )
    parser.add_argument(
        "output", nargs="?", type=arg_output, default=None,
        help="path to directory where the output JSON file(s) should be stored."
    )

    args = parser.parse_args()
    print("DONE", type(args.input), repr(args.input))


if __name__ == "__main__":
    main()
