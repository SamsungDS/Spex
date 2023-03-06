from re import compile as re_compile
from typing import TYPE_CHECKING, Dict, Tuple, Type, Optional, Iterator
from spexs2.xml import Xpath
from spexs2.extractors.valuetable import ValueTableExtractor
from spexs2.extractors.structtable import BitsTableExtractor, BytesTableExtractor
from spexs2.lint import LintEntry, Code, Linter
from spexs2.defs import JSON, Entity, EntityMeta

if TYPE_CHECKING:
    from spexs2.xml import ElementTree, Element
    from spexs2.extractors.figure import FigureExtractor


class DocLinter:
    """
    Records linting issues raised from transforming the HTML to a JSON model.

    Implements the `spexs2.lint.Linter` protocol.
    """
    def __init__(self):
        self._lint_issues = []

    def add_issue(self, code: Code, fig: str, *,
                  msg: Optional[str] = None,
                  row: Optional[str] = None) -> LintEntry:

        l_entry = LintEntry(
            code=code,
            fig=fig,
            msg="" if msg is None else msg,
            row=row
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
    def label_overrides(self) -> Dict[Tuple[str, str], str]:
        return {}

    @property
    def brief_overrides(self) -> Dict[Tuple[str, str], str]:
        return {}

    @staticmethod
    def extractor_defaults() -> Dict[str, Type["FigureExtractor"]]:
        return {
            "values": ValueTableExtractor,
            "bits": BitsTableExtractor,
            "bytes": BytesTableExtractor,
        }

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

    def _on_extract_figure_title(self, tbl: "Element") -> Optional[str]:
        """Extract title from figure table."""
        # title = "".join(Xpath.elem_first_req(tbl, "./tr[1]").itertext()).strip()
        fig_tr = Xpath.elem_first(tbl, "./tr[1]")
        assert fig_tr is not None
        title = "".join(
            e.decode("utf-8") if isinstance(e, bytes) else e
            for e in fig_tr.itertext()).strip()
        # remove entire tr to simplify downstream processing between top-level and
        # nested figures.
        parent = fig_tr.getparent()
        assert parent is not None
        parent.remove(fig_tr)
        return title if "Figure" in title else None

    def _on_extract_figure_id(self, tbl: "Element", figure_title: str) -> str:
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

            figure_title = self._on_extract_figure_title(tbl)
            if figure_title is None:
                continue

            figure_id = self._on_extract_figure_id(tbl, figure_title)
            yield {
                "title": figure_title,
                "fig_id": figure_id,
            }, tbl

    def _get_extractor(self, fig_id: str, tbl: "Element") -> Optional[Type["FigureExtractor"]]:
        e = self.fig_extractor_overrides.get(fig_id, None)
        if e is not None:
            return e
        # Try to extract and normalize the textual value of the first column
        # This typically says something like 'values', 'bytes' or 'bits' from
        # the tables which we are interested in.
        # (NOTE: works on top-level tables also because we removed the figure tr)
        td1 = Xpath.elem_first(tbl, "./tr[1]/*[1]")
        if td1 is None:
            return None
        td1_txt = "".join(
            e.decode("utf-8") if isinstance(e, bytes) else e
            for e in td1.itertext()).lower().strip()
        td1_txt = {
            "byte": "bytes",
            "bit": "bits",
            "value": "values"
        }.get(td1_txt, td1_txt)
        e = self.extractor_defaults().get(td1_txt, None)
        return e  # may be an extractor, may be None

    def _on_parse_fig(self, entity: EntityMeta, tbl: "Element") -> Iterator[Entity]:
        """Parse figure, emitting one or more entities.

        NOTE: a figure table may contain nested tables which themselves
              become separate entities. Hence calling this produces an
              iterator of entities."""
        extractor_cls = self._get_extractor(entity["fig_id"], tbl)
        if extractor_cls is None:
            return

        e = extractor_cls(self, entity, tbl, self._on_parse_fig, self.__linter)
        yield from e()

    def parse(self) -> Iterator[EntityMeta]:
        # for each eligible top-level figure
        for entity, tbl in self.iter_figures():
            # ... produce one or more entities (parsed figures)
            # depending on the figure type and whether it contains nested tables.
            yield from self._on_parse_fig(entity, tbl)


__all__ = ["DocumentParser"]
