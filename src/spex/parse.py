# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Set, TypedDict, cast

from spex.htmlspec.htmlrenderer import SpexHtmlRenderer
from spex.jsonspec import parse
from spex.jsonspec.defs import JSON
from spex.jsonspec.parserargs import ParserArgs
from spex.logging import ULog, logger


class S2Model(TypedDict):
    meta: Dict[str, JSON]
    entities: List[JSON]


class Writer(Protocol):
    def __enter__(self) -> "Writer":
        ...

    def __exit__(self, errtyp, errval, tb):
        ...

    def write_meta(self, key: str, val: JSON) -> None:
        ...

    def write_entity(self, entity: JSON) -> None:
        ...

    @property
    def path(self) -> Optional[Path]:
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

    @property
    def path(self) -> Optional[Path]:
        return None

    def __exit__(self, errtyp, errval, tb):
        # retain UTF-8 characters in output
        res = json.dumps(self._doc, indent=2, ensure_ascii=False).encode("utf-8")
        print(res.decode())
        if errval is not None:
            raise errval


class FileWriter:
    def __init__(self, output: Path, src: Path):
        fname = src.name[: -len(src.suffix)]
        self._output = output / f"{fname}.json"
        self._src = src
        self._dst = open(self._output, "w")
        self._doc: S2Model = {
            "meta": {},
            "entities": [],
        }

    def write_meta(self, key: str, val: JSON) -> None:
        self._doc["meta"][key] = val

    def write_entity(self, entity: JSON) -> None:
        self._doc["entities"].append(entity)

    @property
    def path(self) -> Optional[Path]:
        return self._output

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


def get_writer(src: Path, out_path: Optional[Path]) -> Writer:
    if out_path:
        return FileWriter(out_path, src)
    return StdoutWriter(src)


def parse_spec(spec, args: ParserArgs):
    ignore_lint_codes: Set[str] = set(c.name for c in args.lint_codes_ignore)

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
        sp = SpexHtmlRenderer(docx_path=spec, out_dir=args.output_dir)
        spec = sp.html_path
        try:
            sp.generate()
        finally:
            del sp

    with get_writer(spec, args.output_dir) as w:
        sdoc = parse.open_doc(spec)
        w.write_meta("specification", sdoc.key)
        w.write_meta("revision", sdoc.rev)
        w.write_meta("format version", 1)  # TODO define elsewhere
        dparser = sdoc.get_parser(args)
        for entity in dparser.parse():
            w.write_entity(cast(JSON, entity))

        reported_lint_errs = [
            lint_entry.to_json()
            for lint_entry in dparser.linter.lint_entries()
            if lint_entry.code not in ignore_lint_codes
        ]

        if reported_lint_errs:
            err_prefix = f"Encountered {len(reported_lint_errs)} linting errors during processing"
            if p := w.path:
                err_msg = f"see `{str(p)}`"
            else:
                err_msg = "see output above"
            logger.log(
                ULog.ERROR,
                f"{err_prefix}, {err_msg}",
            )
        w.write_meta("lint", reported_lint_errs)
