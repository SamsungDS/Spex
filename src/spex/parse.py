# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

import json
from pathlib import Path
from typing import (
    Dict,
    Generator,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypeAlias,
    TypedDict,
    cast,
)

from spex.htmlspec.htmlrenderer import SpexHtmlRenderer
from spex.jsonspec import parse
from spex.jsonspec.defs import JSON
from spex.jsonspec.parserargs import ParserArgs
from spex.logging import ULog, logger

ParseProgressStatus: TypeAlias = Tuple[
    str, int, int
]  # (<phase>, <figure>, <of figures>)


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


def parse_spec(
    spec: Path, args: ParserArgs, yield_progress=False
) -> Generator[ParseProgressStatus, None, Optional[Path]]:
    ignore_lint_codes: Set[str] = set(c.name for c in args.lint_codes_ignore)

    if spec.suffix == ".docx":
        sp = SpexHtmlRenderer(docx_path=spec, out_dir=args.output_dir)
        spec = sp.html_path
        try:
            gen = sp.generate(yield_progress=yield_progress)
            if yield_progress:
                num_figures = sp.num_figures
                for fig_ndx in gen:
                    yield ("html", fig_ndx, num_figures)
            else:
                for _ in gen:
                    pass
        finally:
            del sp

    with get_writer(spec, args.output_dir) as w:
        sdoc = parse.open_doc(spec)
        w.write_meta("specification", sdoc.key)
        w.write_meta("revision", sdoc.rev)
        w.write_meta("format version", 1)  # TODO define elsewhere
        dparser = sdoc.get_parser(args)
        if yield_progress:
            num_figures = dparser.num_figures
            for fig_ndx, entity in enumerate(dparser.parse()):
                yield ("json", fig_ndx, num_figures)
                w.write_entity(cast(JSON, entity))
        else:
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
        return w.path  # return path to output JSON
