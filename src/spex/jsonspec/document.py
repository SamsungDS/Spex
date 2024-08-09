# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from re import compile as re_compile
from re import sub
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Tuple, Type, TypeAlias

from loguru import logger

from spex.jsonspec.defs import JSON, Entity, EntityMeta, cast_json
from spex.jsonspec.extractors.structtable import BitsTableExtractor, BytesTableExtractor
from spex.jsonspec.extractors.valuetable import ValueTableExtractor
from spex.jsonspec.lint import LintEntry, Linter, LintErr
from spex.jsonspec.parserargs import ParserArgs
from spex.log import ULog
from spex.xml import XmlUtils, Xpath

if TYPE_CHECKING:
    from spex.jsonspec.extractors.figure import FigureExtractor
    from spex.xml import Element, ElementTree


FigId: TypeAlias = str
FigRow: TypeAlias = str


class DocLinter:
    """
    Records linting issues raised from transforming the HTML to a JSON model.

    Implements the `spexs2.lint.Linter` protocol.
    """

    def __init__(self) -> None:
        self._lint_issues: List[LintEntry] = []

    def add_issue(
        self,
        err: LintErr,
        fig: str,
        *,
        msg: Optional[str] = None,
        row_key: Optional[str] = None,
        ctx: Optional[Dict[str, JSON]] = None,
    ) -> None:
        l_entry = LintEntry(
            err=err,
            fig=fig,
            msg="" if msg is None else msg,
            row=row_key,
            ctx=dict() if ctx is None else ctx,
        )
        self._lint_issues.append(l_entry)

    def lint_entries(self) -> List[LintEntry]:
        return [*self._lint_issues]


class DocumentParser:
    rgx_fig_id = re_compile(r"Figure\s+(?P<figid>[^\s^:]+).*")
    fig_extractor_overrides: Dict[str, Type["FigureExtractor"]] = {}

    def __init__(self, args: ParserArgs, doc: "ElementTree", spec: str, revision: str):
        self.__args = args
        self.__doc = doc
        self.__spec = spec
        self.__revision = revision
        self.__linter = DocLinter()
        self.__post_init__()
        self._unwind_parse_error = False
        self.__fig_id_missing_counter = 0

    def __post_init__(self) -> None:
        ...

    @property
    def args(self) -> ParserArgs:
        """Return CLI args."""
        return self.__args

    @property
    def tbl_normalize_mappings(self) -> Dict[str, str]:
        return {
            "code": "value",
            "bit": "bits",
            "byte": "bytes",
        }

    @property
    def extractors(self) -> List[Type["FigureExtractor"]]:
        """Return list of Figure extractors to try applying to figures found in document

        Note:
            Each extractor's `can_apply` function is called in turn to determine if
            the extractor can be used for a given figure. Note that the first matching
            extractor is used, so order matters.

            Override in custom document extractors to add new "default" extractors to
            attempt applying for each figure found in the document.
        """
        return [
            BytesTableExtractor,
            ValueTableExtractor,
            BitsTableExtractor,
        ]

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
            e.decode("utf-8") if isinstance(e, bytes) else e for e in fig_tr.itertext()
        ).strip()
        return title if "Figure" in title else None

    def _on_extract_figure_id(self, figure_title: str) -> str:
        """Extract figure ID from its title."""
        # Extract figure ID, all figures should have one
        m = self.rgx_fig_id.match(figure_title)
        if m is None:
            logger.log(
                ULog.ERROR,
                f"failed extracting title from figure header {figure_title!r}",
            )
            fig_id = self.__fig_id_missing_counter
            self.__fig_id_missing_counter = fig_id + 1

            self.linter.add_issue(
                LintErr.TBL_FIG_ID_EXTRACT_ERR,
                f"FIG_ID_MISSING[{fig_id}]",
                ctx={"title": figure_title},
            )
            raise RuntimeError(f"failed to extract figure ID from {figure_title!r}")
        return m.group("figid")

    def _figures(self) -> List["Element"]:
        return Xpath.elems(self.doc, "./body/table")

    @property
    def num_figures(self) -> int:
        """Return estimate of number of figures in document.

        NOTE: some figures may be skipped due to missing information
              so this value represents an upper bound on the number of
              figures being processed."""
        return len(self._figures())

    def iter_figures(self) -> Iterator[Tuple[EntityMeta, "Element"]]:
        for tbl in self._figures():
            # Kludge: should be fixed in source documents, but a few tables
            # (Fig202, Fig223 in Base 2.0c spec) are wrapped in an extra table
            inner_tbl = Xpath.elem_first(tbl, "./tr[1]/td[1]/*[1]")
            if inner_tbl is not None and inner_tbl.tag == "table":
                tbl = inner_tbl

            fig_tr = Xpath.elem_first_req(tbl, "./tr[1]")
            # remove entire tr to simplify downstream processing between top-level and
            # nested figures.
            parent = fig_tr.getparent()
            assert parent is not None
            parent.remove(fig_tr)
            figure_title = self._on_extract_figure_title(fig_tr)
            if figure_title is None:
                continue

            try:
                figure_id = self._on_extract_figure_id(figure_title)
            except RuntimeError:
                # see caller - skip figure
                continue
            yield {
                "title": figure_title,
                "fig_id": figure_id,
            }, tbl

    def extract_tbl_headers(self, fig_id: str, tbl: "Element") -> List[str]:
        """Extracts a textual value for each column in the header.

        E.g. ['Range', 'Bit', 'Definition']. This can then be used to infer
        from which fields the value/range, label and data(brief and sub-tables)
        should be extracted.

        Note:
            column headers match one-to-one with the table's columns, this means
            empty strings are also included.

            column headers are lightly normalized - they are lower-cased, stripped
            of surrounding white-space and matches in `tbl_normalize_mappings`
            are replaced.

            If a column header matches an entry in `tbl_normalize_mappings`, it
            is replaced and a linting error is raised, indicating that a common
            variant of the standard table heading for that type was used.
            Some classic examples would be 'bit' instead of 'bits', 'code' instead
            of 'value' or 'definition' instead of 'description'.
        """

        def normalize_hdr(hdr: str) -> str:
            # some headers have newlines and use spaces for indentation, strip
            hdr = sub(" +", " ", hdr.replace("\n", " ").replace("\r", "")).strip()
            replacement = self.tbl_normalize_mappings.get(hdr, None)
            if replacement is not None:
                self.linter.add_issue(
                    LintErr.TBL_HDR_ERR,
                    fig_id,
                    ctx={
                        "got": hdr,
                        "expected": replacement,
                    },
                )
                return replacement
            else:
                return hdr

        return [
            normalize_hdr(XmlUtils.to_text(thdr).lower().strip())
            for thdr in Xpath.elems(tbl, "./tr[1]/*")
        ]

    def _on_parse_fig(self, entity: EntityMeta, tbl: "Element") -> Iterator[Entity]:
        """Parse figure, emitting one or more entities.

        Note:
            a figure table may contain nested tables which themselves
            become separate entities. Hence calling this produces an
            iterator of entities.
        """
        self._unwind_parse_error = False
        fig_id = entity["fig_id"]
        tbl_hdrs = self.extract_tbl_headers(fig_id, tbl)
        extractor_cls = self.fig_extractor_overrides.get(fig_id, None)
        mapping = None

        if extractor_cls is None:
            for ecls in self.extractors:
                mapping = ecls.can_apply(tbl_hdrs)
                if mapping is not None:
                    extractor_cls = ecls
                    break
            if extractor_cls is None:
                self.linter.add_issue(
                    LintErr.TBL_SKIPPED, fig_id, ctx={"columns": cast_json(tbl_hdrs)}
                )
                return
        else:
            # extractor_cls not None, class gotten from override
            mapping = extractor_cls.can_apply(tbl_hdrs)
            if mapping is None:
                raise RuntimeError(
                    "override class failed to detect columns to extract from"
                )

        assert mapping is not None  # only needed to appease type-checking
        e = extractor_cls(
            doc_parser=self,
            entity_meta=entity,
            tbl=tbl,
            tbl_hdrs=tbl_hdrs,
            parse_fn=self._on_parse_fig,
            linter=self.__linter,
            mapping=mapping,
        )
        with logger.contextualize(
            entity=entity,
            doc={"spec": self.spec, "revision": self.revision},
            extractor_cls=extractor_cls.__qualname__,
        ):
            gen = e()
            while True:
                try:
                    yield from gen
                    break
                except Exception as err:
                    if not self._unwind_parse_error:
                        if self.args.verbose:
                            traceback.print_exc()
                        logger.log(ULog.ERROR, f"failed parsing figure {entity!r}")
                        logger.exception("exception when parsing figure")
                        self._unwind_parse_error = True
                        ctx: Dict[str, JSON] = {}
                        if "title" in entity:
                            ctx["title"] = entity["title"]
                        self.linter.add_issue(
                            LintErr.TBL_PARSE_ERR,
                            entity["fig_id"],
                            ctx=ctx,
                        )
                    else:
                        logger.log(ULog.ERROR, f"  in {entity!r}")

                    if (
                        "parent_fig_id" in entity
                        or self.args.skip_fig_on_error is False
                    ):
                        raise err

    def parse(self) -> Iterator[EntityMeta]:
        # for each eligible top-level figure
        for entity, tbl in self.iter_figures():
            # ... produce one or more entities (parsed figures)
            # depending on the figure type and whether it contains nested tables.
            yield from self._on_parse_fig(entity, tbl)


__all__ = ["DocumentParser"]
