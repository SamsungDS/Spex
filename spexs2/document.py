from re import compile as re_compile
from typing import TYPE_CHECKING, Dict, Tuple, Type, Optional, Iterator, List, TypeAlias
from spexs2.xml import Xpath
from spexs2.extractors.valuetable import ValueTableExtractor
from spexs2.extractors.structtable import BitsTableExtractor, BytesTableExtractor
from spexs2.lint import LintEntry, Code, Linter
from spexs2.defs import JSON, Entity, EntityMeta

from spexs2 import xml  # TODO: for debugging

if TYPE_CHECKING:
    from spexs2.xml import ElementTree, Element
    from spexs2.extractors.figure import FigureExtractor


FigId: TypeAlias = str
FigRow: TypeAlias = str


class DocLinter:
    """
    Records linting issues raised from transforming the HTML to a JSON model.

    Implements the `spexs2.lint.Linter` protocol.
    """
    def __init__(self):
        self._lint_issues = []

    def add_issue(self, code: Code, fig: str, *,
                  msg: Optional[str] = None,
                  row: Optional[str] = None,
                  ctx: Optional[Dict[str, JSON]] = None) -> LintEntry:

        l_entry = LintEntry(
            code=code,
            fig=fig,
            msg="" if msg is None else msg,
            row=row,
            ctx=dict() if ctx is None else ctx,
        )
        self._lint_issues.append(l_entry)
        return l_entry

    def to_json(self) -> JSON:
        return [l_entry.to_json() for l_entry in self._lint_issues]


class DocumentParser:
    rgx_fig_id = re_compile(r"Figure\s+(?P<figid>[^\s^:]+).*")
    fig_extractor_overrides: Dict[str, Type["FigureExtractor"]] = {}

    def __init__(self, doc: "ElementTree", spec: str, revision: str):
        self.__doc = doc
        self.__spec = spec
        self.__revision = revision
        self.__linter = DocLinter()
        self.__post_init__()

    def __post_init__(self) -> None:
        ...

    @property
    def label_overrides(self) -> Dict[Tuple[FigId, FigRow], str]:
        """Provide names for fields where none can be extracted/inferred."""
        return {}

    @property
    def brief_overrides(self) -> Dict[Tuple[FigId, FigRow], str]:
        """Provide brief descriptions of fields where none can be extracted/inferred."""
        return {}

    @property
    def spec(self) -> str:
        return self.__spec

    @property
    def revision(self) -> str:
        return self.__revision

    @property
    def doc(self) -> "ElementTree":
        return self.__doc

    @property
    def linter(self) -> Linter:
        return self.__linter

    def _on_extract_figure_title(self, fig_tr: "Element") -> Optional[str]:
        """Extract title from figure table."""
        assert fig_tr is not None
        title = "".join(
            e.decode("utf-8") if isinstance(e, bytes) else e
            for e in fig_tr.itertext()).strip()
        return title if "Figure" in title else None

    def _on_extract_figure_id(self, figure_title: str) -> str:
        """Extract figure ID from its title."""
        # Extract figure ID, all figures should have one
        m = self.rgx_fig_id.match(figure_title)
        assert m is not None, f"failed to extract figure ID from {figure_title}"
        return m.group("figid")

    def iter_figures(self) -> Iterator[Tuple[EntityMeta, "Element"]]:
        for tbl in Xpath.elems(self.doc, "./body/table"):
            # Kludge: should be fixed in source documents, but a few tables
            # (Fig202, Fig223 in Base 2.0c spec) are wrapped in an extra table
            inner_tbl = Xpath.elem_first(tbl, "./tr[1]/td[1]/*[1]")
            if inner_tbl is not None and inner_tbl.tag == "table":
                tbl = inner_tbl

            fig_tr = Xpath.elem_first(tbl, "./tr[1]")
            # remove entire tr to simplify downstream processing between top-level and
            # nested figures.
            parent = fig_tr.getparent()
            assert parent is not None
            parent.remove(fig_tr)
            figure_title = self._on_extract_figure_title(fig_tr)
            if figure_title is None:
                continue

            figure_id = self._on_extract_figure_id(figure_title)
            yield {
                "title": figure_title,
                "fig_id": figure_id,
            }, tbl

    def extract_tbl_headers(self, tbl: "Element") -> List[str]:
        """Extracts a textual value for each column in the header.

        E.g. ['Range', 'Bit', 'Definition']. This can then be used to infer
        from which fields the value/range, label and data(brief and sub-tables)
        should be extracted.

        Note: empty strings are retained, this means each element's offset directly
              corresponds to the offset of the actual column."""
        thdrs = Xpath.elems(tbl, "./tr[1]/*")
        return [
            xml.to_text(thdr) for thdr in thdrs
        ]

    def normalize_tbl_headers(self, fig_id: str, thdrs: List[str]) -> List[str]:
        """Normalizes table headers

        NOTE: raises lint issues when encountering non-standard variants of established column
              names ('bit' instead of 'bits', 'definition' instead of 'description')."""
        thdrs = [thdr.lower().strip() for thdr in thdrs]

        def normalize_hdr(hdr: str) -> str:
            if hdr == "byte":
                self.linter.add_issue(Code.T1006, fig_id, ctx={
                    f"{Code.T1006.name}.header": "byte"
                })
                return "bytes"
            elif hdr == "bit":
                self.linter.add_issue(Code.T1006, fig_id, ctx={
                    f"{Code.T1006.name}.header": "byte"
                })
                return "bits"
            elif hdr == "code":
                self.linter.add_issue(Code.T1006, fig_id, ctx={
                    f"{Code.T1006.name}.header": "byte"
                })
                return "value"
            elif hdr == "definition":
                self.linter.add_issue(Code.T1006, fig_id, ctx={
                    f"{Code.T1006.name}.header": "byte"
                })
                return "description"
            return hdr

        return [
            normalize_hdr(hdr)
            for hdr in thdrs
        ]

    def _infer_extractor_from_hdrs(self, hdrs: List[str]) -> Optional[Type["FigureExtractor"]]:
        """Examines header headings and determines which extractor to use.

        NOTE: this is consulted after specific overrides given in `fig_extractor_overrides`.
              Typically, you want to set specific overrides, not re-implement this method.
        NOTE: If you re-implement this method, take care to create linting issues for non-standard
              column names (like 'bit' instead of 'bits)..
        """
        if "bytes" in hdrs:
            return BytesTableExtractor
        elif "bits" in hdrs:
            return BitsTableExtractor
        elif "value" in hdrs:
            return ValueTableExtractor
        else:
            # no idea what to do with this table. And this might well be OK, many tables are one-off
            # and not relevant for this model.
            return None

    def _on_parse_fig(self, entity: EntityMeta, tbl: "Element") -> Iterator[Entity]:
        """Parse figure, emitting one or more entities.

        NOTE: a figure table may contain nested tables which themselves
              become separate entities. Hence calling this produces an
              iterator of entities."""
        fig_id = entity["fig_id"]
        tbl_hdrs = self.normalize_tbl_headers(fig_id, self.extract_tbl_headers(tbl))
        extractor_cls = self.fig_extractor_overrides.get(fig_id, None)
        if extractor_cls is None:
            extractor_cls = self._infer_extractor_from_hdrs(tbl_hdrs)
            if extractor_cls is None:
                return

        e = extractor_cls(
            doc_parser=self,
            entity_meta=entity,
            tbl=tbl,
            tbl_hdrs=tbl_hdrs,
            parse_fn=self._on_parse_fig,
            linter=self.__linter
        )
        yield from e()

    def parse(self) -> Iterator[EntityMeta]:
        # for each eligible top-level figure
        for entity, tbl in self.iter_figures():
            # ... produce one or more entities (parsed figures)
            # depending on the figure type and whether it contains nested tables.
            yield from self._on_parse_fig(entity, tbl)


__all__ = ["DocumentParser"]
