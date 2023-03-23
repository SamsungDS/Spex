import argparse
import json
from pathlib import Path
import textwrap
from typing import Protocol, Dict, TypedDict, List
from spex.model import parse
from spex.model.defs import JSON
from spex.model.lint import Code


class S2Model(TypedDict):
    meta: Dict[str, JSON]
    entities: List[JSON]


def arg_input(arg: str) -> Path:
    p = Path(arg)
    if not p.exists():
        raise RuntimeError(f"no file at '{p}'")
    elif not p.is_file():
        raise RuntimeError(f"path '{p}' exists, but is not a file")
    return p


def arg_output(arg: str) -> Path:
    p = Path(arg)
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)
    if not p.is_dir():
        raise RuntimeError(f"output must be a directory (or omitted)")

    return p


def arg_lintcode(arg: str) -> List[Code]:
    return [Code[c.strip().upper()] for c in arg.split(",")]


class Writer(Protocol):
    def __enter__(self) -> "Writer": ...
    def __exit__(self, errtyp, errval, tb): ...
    def write_meta(self, key: str, val: JSON) -> None: ...
    def write_entity(self, entity: JSON) -> None: ...


class StdoutWriter(Writer):
    def __init__(self, src: Path):
        self._src = src
        self._doc: S2Model = {
            "meta": {},
            "entities": [],
        }

    def write_meta(self, key: str, val: JSON) -> None:
        self._doc["meta"][key] = val

    def write_entity(self, entity: JSON) -> None:
        self._doc["entities"].append(entity)

    def __enter__(self) -> "Writer":
        return self

    def __exit__(self, errtyp, errval, tb):
        # retain UTF-8 characters in output
        res = json.dumps(self._doc, indent=2, ensure_ascii=False).encode("utf-8")
        print(res.decode())
        if errval is not None:
            raise errval


class FileWriter:
    def __init__(self, output: Path, src: Path):
        self._output = output
        self._src = src
        fname = src.name[:-len(src.suffix)]
        _dst = output / f"{fname}.json"
        self._dst = open(_dst, "w")
        self._doc: S2Model = {
            "meta": {},
            "entities": [],
        }

    def write_meta(self, key: str, val: JSON) -> None:
        self._doc["meta"][key] = val

    def write_entity(self, entity: JSON) -> None:
        self._doc["entities"].append(entity)

    def __enter__(self) -> "Writer":
        return self

    def __exit__(self, errtyp, errval, tb):
        try:
            json.dump(self._doc, self._dst, indent=2, ensure_ascii=False)
        finally:
            self._dst.close()
        self._dst = None
        if errval is not None:
            raise errval


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
        "-o", "--output", type=arg_output, default=None,
        help="path to directory where the output JSON file(s) should be stored."
    )
    parser.add_argument(
        "--lint-ignore", type=arg_lintcode, default=[]
    )

    args = parser.parse_args()

    def get_writer(src: Path) -> Writer:
        if args.output:
            return FileWriter(args.output, src)
        return StdoutWriter(src)

    for spec in args.input:
        with get_writer(spec) as w:
            print(f"Parsing '{spec}'...")
            sdoc = parse.open_doc(spec)
            w.write_meta("specification", sdoc.key)
            w.write_meta("revision", sdoc.rev)
            w.write_meta("format version", 1)  # TODO define elsewhere
            dparser = sdoc.get_parser()
            for entity in dparser.parse():
                w.write_entity(entity)

            ignore_lint_codes = set(c.name for c in args.lint_ignore)
            w.write_meta("lint", [
                lint_err for lint_err in dparser.linter.to_json()
                if lint_err["code"] not in ignore_lint_codes
            ])


if __name__ == "__main__":
    main()
