from dataclasses import dataclass
from typing import Optional, Union, List as TList, Iterator, Dict, Set
from lxml.etree import _Element
from spex.htmlmodel.docx import RunProperties, AbstractNumLvl, Tag, TableWrap, Document
from spex.xml import Xpath

from spex.htmlmodel.stream import Stream


@dataclass(frozen=True)
class TcPr:
    shd_fill: Optional[str]

    @property
    def css_attrs(self) -> Dict[str, str]:
        if self.shd_fill in ("None", "auto"):
            return {}
        return {"background-color": f"#{self.shd_fill}"}


@dataclass(frozen=True)
class Span:
    style: Optional[RunProperties]
    text: str


@dataclass(frozen=True)
class Paragraph:
    spans: TList[Span]


@dataclass(frozen=True)
class ListElem:
    elems: TList[Span]


@dataclass(frozen=True)
class List:
    props: AbstractNumLvl
    elems: TList[Union[ListElem, "List"]]

    @property
    def tag(self) -> str:
        return self.props.tag


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class TableCell:
    tag: str
    elems: TList[Union[List, Paragraph, Span, "Table"]]
    span: Point
    origin: Point
    tc_pr: Optional[TcPr]


@dataclass(frozen=True)
class Table:
    rows: TList[TList[TableCell]]


class SpexParser:
    def __init__(self, document: Document):
        self._document = document
        self.__tbls_seen: Set[_Element] = set()

    def parse(self) -> Iterator[Table]:
        self.__tbls_seen = set()
        stream = Stream(t for t in self._document.tables)
        while not stream.end():
            tbl = self._parse_table(stream)
            if tbl is not None:
                yield tbl

    def _parse_any(
        self, stream: Stream[_Element]
    ) -> Iterator[Union[List, Paragraph, Table]]:
        while not stream.end():
            current = stream.peek()
            if current.tag == Tag.tbl.value:
                tbl = self._parse_table(stream)
                if tbl:
                    yield tbl
            elif current.tag == Tag.p.value:
                if self.__p_is_list_paragraph(current):
                    yield self._parse_list(stream)
                else:
                    p = self._parse_paragraph(stream)
                    if p:
                        yield p
            else:
                stream.consume()

    def __p_is_list_paragraph(self, e: _Element):
        num_id = Xpath.attr_first(e, "./w:pPr/w:numPr/w:numId/@w:val")
        if num_id is None or self._document.numbering_xml is None:
            return False
        return self._document.numbering_xml.has_num_id(num_id)

    def _parse_list(self, stream: Stream[_Element]) -> List:
        current = stream.peek()
        assert current.tag == Tag.p.value, f"assumed w:p tag, got {current.tag!r}"

        num_id = int(Xpath.attr_first_req(current, "./w:pPr/w:numPr/w:numId/@w:val"))

        assert (
            self._document.numbering_xml is not None
        ), "cannot have numbering styles w/o a numbering document"
        style = self._document.numbering_xml.get_style(num_id)

        ilvl = int(Xpath.attr_first_req(current, "./w:pPr/w:numPr/w:ilvl/@w:val"))
        slvl = style.get_ilvl(ilvl)

        return List(
            props=slvl,
            elems=list(self._parse_list_elems(stream, style.abstract_num_id, ilvl)),
        )

    def _parse_list_elems(
        self, stream: Stream[_Element], abstract_num_id: int, ilvl: int
    ) -> Iterator[Union[ListElem, List]]:
        # TODO: refac - style to just abstract_num_id: int, nothing more needed
        num_doc = self._document.numbering_xml
        assert (
            num_doc is not None
        ), "cannot have a numbering style w/o a numbering document"
        while not stream.end():
            child = stream.peek()
            if child is None:
                break

            if child.tag != Tag.p.value:
                break  # not a paragraph tag, assume end of list

            if not self.__p_is_list_paragraph(child):
                # not a list paragraph
                break

            num_id = int(Xpath.attr_first_req(child, "./w:pPr/w:numPr/w:numId/@w:val"))
            if num_doc.get_style(num_id).abstract_num_id != abstract_num_id:
                # different list
                break

            child_ilvl = int(
                Xpath.attr_first_req(child, "./w:pPr/w:numPr/w:ilvl/@w:val")
            )
            if child_ilvl > ilvl:
                # nested list
                yield self._parse_list(stream)
                continue
            elif child_ilvl < ilvl:
                # pop out to parent list
                break

            elem = stream.consume()
            yield ListElem(elems=list(self._parse_spans(elem)))

    def _parse_paragraph(self, stream: Stream[_Element]) -> Optional[Paragraph]:
        # pStyle == "normal" -> normal text paragraph
        current = stream.consume()
        spans = list(self._parse_spans(current))
        if len(spans) > 0:
            return Paragraph(spans=list(self._parse_spans(current)))
        return None

    def _select_runs(self, p: _Element) -> Iterator[_Element]:
        # we also want to extract text from hyperlinks, so loop over top-level
        # children, extracting runs (w:r) and hyperlinks (w:hyperlink)
        # if a hyperlink, strip and yield the run.
        # TODO: works, but need to satisfy mypy somehow...
        # for child in p.iterchildren(Tag.r.value, Tag.hyperlink.value):
        for child in p.iterchildren():
            if child.tag == Tag.r.value:
                yield child
            elif child.tag == Tag.hyperlink.value:
                yield Xpath.elem_first_req(child, "./w:r")

    def _parse_spans(self, p: _Element) -> Iterator[Span]:
        for r in self._select_runs(p):
            txt = Xpath.elem_first(r, "./w:t")
            if txt is None or txt.text is None:
                continue
            r_rpr = self._document.extract_r_rpr(r)
            yield Span(style=r_rpr, text=txt.text)

    def _parse_table(self, stream: Stream[_Element]) -> Optional[Table]:
        tbl = stream.consume()
        assert tbl.tag == Tag.tbl.value, f"expected table (w:tbl), got {tbl.tag}"
        if tbl in self.__tbls_seen:
            # small hack. When we iterate over all figures (tables), we will
            # also select the nested tables.
            # This skips listing the table twice while ensuring that we can still
            # use the selector which extracts tables regardless of how deeply
            # nested they are.
            return None
        self.__tbls_seen.add(tbl)
        tw = TableWrap(tbl)
        rows: TList[TList[TableCell]] = []
        cell_cache: Dict[Point, TableCell] = {}
        for rndx, row in enumerate(tw.grid()):
            cells: TList[TableCell] = []
            for cndx, gridcell in enumerate(row):
                p = Point(cndx, rndx)
                tcell = cell_cache.get(p, None)
                if tcell is not None:
                    cells.append(tcell)
                    continue

                shd_fill = Xpath.attr_first(gridcell.cell, "./w:tcPr/w:shd/@w:fill")
                tag = "td"
                # could check for a color with a regex, but not yet necessary.
                # require hex code (filters out 'auto' which we can ignore).
                if shd_fill and shd_fill.lower() and len(shd_fill) == 6:
                    tcpr = (
                        TcPr(shd_fill=shd_fill)
                        if shd_fill.lower() != "ffffff"
                        else None
                    )
                else:
                    tcpr = None
                if (
                    tcpr is not None
                    and shd_fill is not None
                    and (shd_fill[0:2] == shd_fill[2:4] == shd_fill[4:6])
                ):
                    # heuristic: specs uses various greytone colors to mark table headers
                    tag = "th"

                tcell = TableCell(
                    elems=list(
                        self._parse_any(Stream(e for e in gridcell.cell.iterchildren()))
                    ),
                    span=Point(gridcell.colspan, gridcell.rowspan),
                    origin=Point(gridcell.left, gridcell.top),
                    tc_pr=tcpr,
                    tag=tag,
                )
                cell_cache[p] = tcell
                cells.append(tcell)
            rows.append(cells)
        return Table(rows=rows)
