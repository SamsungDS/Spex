import sys
import argparse
import json
from pathlib import Path
import textwrap
from typing import Protocol, Dict, TypedDict, List
from spex.model import parse
from spex.model.defs import JSON
from spex.model.lint import Code
from spex.htmlmodel.htmlrenderer import SpexHtmlRenderer


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
    def __enter__(self) -> "Writer":
        ...

    def __exit__(self, errtyp, errval, tb):
        ...

    def write_meta(self, key: str, val: JSON) -> None:
        ...

    def write_entity(self, entity: JSON) -> None:
        ...


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
        fname = src.name[: -len(src.suffix)]
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
    lint_codes = "\n".join(f"      * {entry.name}  - {entry.value}" for entry in Code)
    epilog = textwrap.dedent(
        f"""
    Notes:
    ~~~~~~
    * Linting:
      During production of the NVMe-model, a number of linting codes are raised.
      These signify potential and definite issues encountered when parsing the
      source HTML model, in turn derived from the docx specification document.

      You may choose to ignore classes of errors during processing. 
      For instance, to ignore lint errors of code T1000 and T1001, add the
      following to your command: `--lint-ignore=T1000,T1001`.

      The linting codes, and their general meaning, are as follows:
      ---
{lint_codes}
      ---
    * output:
      if `output` is a directory, then any output(s) generated from processing
      (NVMe (JSON) models, HTML models, CSS files) will be placed in the
      specified directory. If `output` is omitted, files will be placed into the
      current working directory.
    """
    )
    parser = argparse.ArgumentParser(
        description="Extract data-structures from .docx spec or HTML model",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input",
        nargs="+",
        type=arg_input,
        help="One or more .docx specifications or HTML models to extract data-structures from",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=arg_output,
        default=None,
        help="path to directory where the resulting file(s) should be stored.",
    )
    parser.add_argument("--lint-ignore", type=arg_lintcode, default=[])

    args = parser.parse_args()

    def get_writer(src: Path) -> Writer:
        if args.output:
            return FileWriter(args.output, src)
        return StdoutWriter(src)

    # if no explicit output directory is specified, use the current working directory
    if args.output is None:
        args.output = Path.cwd()

    ignore_lint_codes = set(c.name for c in args.lint_ignore)

    for spec in args.input:
        print(f"Parsing '{spec}'...")

        if spec.suffix == ".json":
            # lint code filtering is applied at the point of writing the lint errors
            # into the resulting NVMe (JSON) model.
            sys.stderr.write(
                "cannot operate on NVMe model (JSON), requires the HTML model or docx spec as input\n"
            )
            sys.stderr.flush()
            sys.exit(1)

        if spec.suffix not in (".html", ".docx"):
            sys.stderr.write(
                f"invalid input file ({spec!s}), requires a HTML model or the docx specification file\n"
            )
            sys.stderr.flush()
            sys.exit(1)

        if spec.suffix == ".docx":
            sp = SpexHtmlRenderer(docx_path=spec, out_dir=args.output)
            spec = sp.html_path
            try:
                sp.generate()
            finally:
                del sp

        with get_writer(spec) as w:
            sdoc = parse.open_doc(spec)
            w.write_meta("specification", sdoc.key)
            w.write_meta("revision", sdoc.rev)
            w.write_meta("format version", 1)  # TODO define elsewhere
            dparser = sdoc.get_parser()
            for entity in dparser.parse():
                w.write_entity(entity)

            w.write_meta(
                "lint",
                [
                    lint_err
                    for lint_err in dparser.linter.to_json()
                    if lint_err["code"] not in ignore_lint_codes
                ],
            )


if __name__ == "__main__":
    main()
