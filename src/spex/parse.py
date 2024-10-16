# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path
from typing import Generator, Optional, Set, cast

from spex import __version__
from spex.htmlspec.htmlrenderer import SpexHtmlRenderer
from spex.jsonspec import parse
from spex.jsonspec.defs import JSON
from spex.jsonspec.parserargs import ParserArgs
from spex.log import ULog, logger
from spex.progressbar import ParseProgressStatus
from spex.writer import FileWriter, StdoutWriter, Writer


def get_writer(src: Path, out_path: Optional[Path]) -> Writer:
    if out_path:
        return FileWriter(out_path, src)
    return StdoutWriter(src)


def parse_spec(
    spec: Path, args: ParserArgs, yield_progress: bool = False
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
        w.write_meta("spex version", __version__)  # TODO define elsewhere
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
            err_prefix = (
                f"Encountered {len(reported_lint_errs)} "
                "linting errors during processing"
            )
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
