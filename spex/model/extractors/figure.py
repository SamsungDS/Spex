from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Optional, Iterator, Tuple, List, Dict
from spex.xml import Element, Xpath
from spex.model.lint import Linter, LintErr
from spex.model.defs import JSON
from spex.model.rowiter import row_iter


if TYPE_CHECKING:
    from spex.model.defs import EntityMeta, ParseFn, Entity
    from spex.model.document import DocumentParser


RowResult = Tuple[Element, Element, Element]


class RowErrPolicy(Enum):
    Stop = 0
    Continue = 1
    Raise = 2


class FigureExtractor(ABC):
    BRIEF_MAXLEN: int = 60
    __linter: Linter

    def __init__(self, *,
                 doc_parser: "DocumentParser",
                 entity_meta: "EntityMeta",
                 tbl: Element,
                 tbl_hdrs: List[str],
                 parse_fn: "ParseFn",
                 linter: Linter):
        self.doc_parser = doc_parser
        self.__entity_meta = entity_meta
        self.__tbl = tbl
        self.__tbl_hdrs = tbl_hdrs
        self._parse = parse_fn
        self.__linter = linter
        self.__post_init__()

    def __post_init__(self) -> None:
        ...

    @property
    def entity_meta(self) -> "EntityMeta":
        return self.__entity_meta

    @property
    def fig_id(self) -> str:
        return self.__entity_meta["fig_id"]

    @property
    def tbl(self) -> Element:
        return self.__tbl

    @property
    def tbl_hdrs(self) -> List[str]:
        return self.__tbl_hdrs

    @property
    def parent_fig_id(self) -> Optional[str]:
        return self.__entity_meta.get("parent_fig_id", None)

    @property
    def title(self) -> Optional[str]:
        return self.__entity_meta.get("title", None)

    @property
    def linter(self) -> Linter:
        return self.__linter

    def add_issue(self, err: LintErr, *,
                  fig: Optional[str] = None,
                  msg: str = "",
                  row_key: Optional[str] = None,
                  ctx: Optional[Dict[str, JSON]] = None) -> None:
        self.__linter.add_issue(err,
                                fig if fig is not None else self.fig_id,
                                msg=msg, row_key=row_key, ctx=ctx)

    def row_iter(self) -> Iterator[Element]:
        # select first td where parent is a tr
        # ... then select the parent (tr) again
        # -> filters out header (th) rows
        yield from row_iter(self.tbl)

    def extract_data_subtbls(self, entity_base: "EntityMeta", data: Element) -> Iterator["Entity"]:
        tbls = Xpath.elems(data, "./table")
        assert len(tbls) <= 1, "invariant broken - expected each field to have at most 1 sub-table"
        if len(tbls) == 0:
            return
        else:
            yield from self._parse(entity_base, tbls[0])

    @abstractmethod
    def __call__(self) -> Iterator["Entity"]:
        # must drive the process from this fn
        ...

    @classmethod
    @abstractmethod
    def can_apply(cls, tbl_col_hdrs: List[str]) -> bool:
        """determine if extractor can be used given the table's column headers.

        Note:
            this function is not called when extractor is provided explicitly
            as an override for some figure.

        Args:
            tbl_col_hdrs: the table's column headers, lower-cased and stripped.

        Returns:
            True iff. extractor is applicable, False otherwise.
        """
        ...

    @staticmethod
    def content_column_hdrs() -> List[str]:
        """Return prioritized list of column headers where extractor should extract the row's content.

        The content row is where the extractor will extract a brief (short documentation string)
        for the row and any sub-tables, if present.
        Also, if there is no dedicated column for row names, these too will be extracted from this column.

        Note:
            First match found in figure's actual table headers is used.

            This is intended to be overridden for specialized extractors where the content
            column is using a non-standard heading.
        """
        return ["description"]

    @staticmethod
    def label_column_hdrs() -> List[str]:
        """Return prioritized list of column headers where extractor should extract the row's name.

        Note:
            First match found in figure's actual table headers is used.

            This is intended to be overridden for specialized extractors where the label
            column is using a non-standard heading.
        """
        return ["attribute", "description"]
