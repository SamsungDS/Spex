# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from html import escape as html_escape
from pathlib import Path
from typing import Any, Generator, Optional, Set, Tuple, TypeAlias

from gcgen.api import Section, write_file
from lxml.etree import _Element

from spex.htmlspec import css
from spex.htmlspec.docx import Document
from spex.htmlspec.parser import (
    List,
    ListElem,
    Paragraph,
    Point,
    Span,
    SpexParser,
    Table,
)

ProgressStatus: TypeAlias = Tuple[int, int]  # processing figure X of Y figures


# TODO: nicer way of using `write_file` ?
class SpexHtmlRenderer:
    def __init__(self, docx_path: Path, out_dir: Optional[Path] = None):
        self._fname = docx_path.name[: -len(docx_path.suffix)]
        self._docx_path = docx_path = docx_path.resolve()
        self._document = Document(docx_path)
        self._parser = SpexParser(self._document)

        if out_dir is None:
            out_dir = docx_path.parent

        self._html_path = out_dir / f"{self._fname}.html"
        self._html_writer = write_file(self._html_path)
        self._html_head = Section()
        self._html_body = Section()
        self._html_doc: Section = self._html_writer.__enter__()

        self._css_path = out_dir / f"{self._fname}.css"
        self._css_writer = write_file(self._css_path)
        self._css_doc: Section = self._css_writer.__enter__()
        # from props -> name
        self._css_txtfmt_cache = css.CssCache("txtfmt")

        self.__css_tcell_cache = css.CssCache("tcell")
        self._destroyed = False

        self.__tbls_seen: Set[_Element] = set()

    def __write_css_prelude(self):
        s = self._css_doc
        css.css_block(
            s,
            "body",
            {
                "font-family": "sans-serif",
            },
        )
        css.css_block(s, "p:first-child", {"margin-top": ".3em"})
        css.css_block(s, "p:last-child", {"margin-bottom": ".3em"})
        css.css_block(
            s,
            "p",
            {
                "margin-top": "0em",
                "margin-left": ".2em",
                "margin-right": ".2em",
            },
        )
        css.css_block(
            s,
            ["table", "td", "th"],
            {
                "border-collapse": "collapse",
                "border": "1px solid black;",
            },
        )
        css.css_block(
            s,
            "table",
            {
                "margin-left": ".3em",
                "margin-right": ".3em",
                "margin-bottom": "3em",
                "margin-top": "1em",
            },
        )
        css.css_block(
            s,
            "td table",
            {
                "margin-bottom": "1em",
            },
        )
        num_xml = self._document.numbering_xml
        if num_xml:
            s.emitln("/* list-formatting styles */")
            for nstyle in self._document.numbering_xml.iter_styles():
                for ilvl in nstyle.ilvls:
                    s.emitln(ilvl.to_css())

    def __write_css_epilog(self):
        # write out cached styles
        s = self._css_doc
        s.emitln("/* text-formatting styles */")
        self._css_txtfmt_cache.emit_rules(s)
        s.emitln("/* table cell formatting styles */")
        self.__css_tcell_cache.emit_rules(s)

    def generate(self, yield_progress=False) -> Generator[int, None, None]:
        """main entrypoint for generator.

        Args:
          * yield_progress (bool): whether to progress status tuples.
                Can be used to implement e.g. progress bars.
        """
        # TODO: really should not be called twice.
        # write prelude for CSS document
        self.__write_css_prelude()

        s = self._html_doc
        s.emitln("<!DOCTYPE html>")
        s.emitln('<html lang="en">')
        s.emitln("<head>").indent()
        title = self._document.header.title
        revision = self._document.header.revision
        s.emit(f'<meta charset="utf-8" data-spec="{title}"')
        if revision is not None:
            s.emit(f' data-revision="{revision}"')
        s.emitln("/>")
        s.emitln(f"<title>{self._fname}</title>")
        s.add_section(self._html_head)
        s.emitln(f'<link rel="stylesheet" href="{self._fname}.css"/>')
        s.dedent().emitln("</head>")
        s.emitln("<body>").indent()
        s.add_section(self._html_body)

        if yield_progress:
            for ndx, tbl in enumerate(self._parser.parse()):
                yield ndx
                self._render_table(s, tbl)
        else:
            for tbl in self._parser.parse():
                self._render_table(s, tbl)

        s.dedent().emitln("</body>")
        s.emitln("</html>")

        self.__write_css_epilog()

    def _render_paragraph(self, s: Section, p: Paragraph) -> None:
        s.emitln("<p>").indent()
        for span in p.spans:
            self._render_span(s, span)
        s.dedent().emitln("</p>")

    def _render_span(self, s: Section, span: Span) -> None:
        txt = html_escape(span.text)
        if span.style is not None:
            clsname = self._css_txtfmt_cache.get_clsname(span.style)
        else:
            clsname = None
        if clsname is not None:
            s.emit(f'<span class="{clsname}">{txt}</span>')
        else:
            s.emit(f"<span>{txt}</span>")

    def _render_list(self, s: Section, lst: List) -> None:
        s.emitln(f'<{lst.tag} class="{lst.props.css_clsname}">').indent()
        open_elem = False
        for elem in lst.elems:
            if isinstance(elem, ListElem):
                if open_elem:
                    s.dedent().emitln("</li>")
                s.emitln("<li>").indent()
                for span in elem.elems:
                    self._render_span(s, span)
                open_elem = True
            elif isinstance(elem, List):
                if not open_elem:
                    s.emitln("<li>").indent()
                self._render_list(s, elem)
                s.dedent().emitln("</li>")
                open_elem = False
            else:
                raise RuntimeError(f"unknown list element {type(elem)}")
        if open_elem:
            s.dedent().emitln("</li>")
        s.dedent().emitln(f"</{lst.tag}>")

    def _render_table(self, s: Section, tbl: Table) -> None:
        s.emitln("<table>").indent()
        for rndx, row in enumerate(tbl.rows):
            s.emitln("<tr>").indent()
            for cndx, cell in enumerate(row):
                pos = Point(cndx, rndx)
                if cell.origin != pos:
                    # cells may span multiple columns and rows, render them only
                    # the first time seen / at its origin point
                    continue
                if cell.tc_pr:
                    clsname = self.__css_tcell_cache.get_clsname(cell.tc_pr)
                else:
                    clsname = None
                s.emit(
                    "<",
                    cell.tag,
                    f' colspan="{cell.span.x}"' if cell.span.x > 1 else "",
                    f' rowspan="{cell.span.y}"' if cell.span.y > 1 else "",
                    f' class="{clsname}"' if clsname else "",
                    ">",
                ).indent()
                for elem in cell.elems:
                    self._render_any(s, elem)
                s.dedent().emitln(f"</{cell.tag}>")
            s.dedent().emitln("</tr>")
        s.dedent().emitln("</table>")

    def _render_any(self, s: Section, o: Any) -> None:
        if isinstance(o, Span):
            self._render_span(s, o)
        elif isinstance(o, Paragraph):
            self._render_paragraph(s, o)
        elif isinstance(o, List):
            self._render_list(s, o)
        elif isinstance(o, Table):
            self._render_table(s, o)
        else:
            raise RuntimeError(f"render got element of type {type(o)} - cannot render")

    @property
    def html_path(self) -> Path:
        """output path of the HTML document resulting from parsing the specification."""
        return self._html_path

    @property
    def css_path(self) -> Path:
        """output path of the CSS sheet accompanying the output HTML page."""
        return self._css_path

    @property
    def num_figures(self) -> int:
        """return number of figures in the document being parsed.

        NOTE: some figures may be skipped during processing for various reasons.
              This thus represents an upper-bound on the number of figures to
              process."""
        return len(self._document.tables)

    def __del__(self):
        if self._destroyed:
            return
        try:
            self._css_writer.__exit__(None, None, None)
            self._css_doc = None
            self._html_writer.__exit__(None, None, None)
            self._html_doc = None
        except Exception as e:
            print(e)
