# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Tuple

from spex.jsonspec.defs import JSON
from spex.jsonspec.extractors.helpers import (
    StructTableMapping,
    ValueTableMapping,
    mapping_incomplete,
)
from spex.jsonspec.lint import Linter, LintErr
from spex.jsonspec.rowiter import row_iter
from spex.xml import Element, Xpath

if TYPE_CHECKING:
    from spex.jsonspec.defs import Entity, EntityMeta, ParseFn
    from spex.jsonspec.document import DocumentParser
    from spex.jsonspec.extractors.helpers import Mapping


RowResult = Tuple[Element, Element, Element]


class RowErrPolicy(Enum):
    Stop = 0
    Continue = 1
    Raise = 2


class FigureExtractor(ABC):
    BRIEF_MAXLEN: int = 60
    __linter: Linter

    def __init__(
        self,
        *,
        doc_parser: "DocumentParser",
        entity_meta: "EntityMeta",
        tbl: Element,
        tbl_hdrs: List[str],
        parse_fn: "ParseFn",
        linter: Linter,
        mapping: Optional[ValueTableMapping | StructTableMapping] = None,
    ):
        self.doc_parser = doc_parser
        self.__entity_meta = entity_meta
        self.__tbl = tbl
        self.__tbl_hdrs = tbl_hdrs
        self._parse = parse_fn
        self.__linter = linter
        self.__post_init__()

    def __post_init__(self) -> None: ...

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

    def add_issue(
        self,
        err: LintErr,
        *,
        fig: Optional[str] = None,
        msg: str = "",
        row_key: Optional[str] = None,
        ctx: Optional[Dict[str, JSON]] = None,
    ) -> None:
        self.__linter.add_issue(
            err,
            fig if fig is not None else self.fig_id,
            msg=msg,
            row_key=row_key,
            ctx=ctx,
        )

    def row_iter(self) -> Iterator[Element]:
        # select first td where parent is a tr
        # ... then select the parent (tr) again
        # -> filters out header (th) rows
        yield from row_iter(self.tbl)

    def extract_data_sub_table(
        self, entity_base: "EntityMeta", data: Element
    ) -> Iterator["Entity"]:
        tbls = Xpath.elems(data, "./table")
        if len(tbls) == 0:
            return
        for tbl in tbls:
            yield from self._parse(entity_base, tbl)

    @abstractmethod
    def __call__(self) -> Iterator["Entity"]:
        # must drive the process from this fn
        ...

    @classmethod
    def can_apply(cls, tbl_col_hdrs: List[str]) -> Optional["Mapping"]:
        """determine if extractor can be used given the table's column headers.

        Note:
            If you want to customize whether an extractor can be applied or not,
            then override `_can_apply` instead of this, probably calling the
            base class' `_can_apply` method and adjusting it as necessary.

            This method is there to catch (for all) that an extractor can only
            be applied if all the semantic components the extractor cares for
            have been identified.

        Args:
            tbl_col_hdrs: the table's column headers, lower-cased and stripped.

        Returns:
            If extractor can be used, returns a Mapping where each semantic component
            is mapped to a concrete column in the figure.
            A semantic components is any type of information the extractor
            extracts with an eye toward generating a normalized representation of the
            struct or enumeration. These components are typically labels, which we
            use to name fields, content (textual description, sometimes used for
            comments in the data-structure) and a value or bit-/byte-range.
        """
        mapping = cls._can_apply(tbl_col_hdrs)
        if mapping_incomplete(mapping):
            return None

        return mapping

    @classmethod
    @abstractmethod
    def _can_apply(cls, tbl_col_hdrs: List[str]) -> "Mapping":
        """determine if extractor can be used given the table's column headers.

        Args:
            tbl_col_hdrs: the table's column headers, lower-cased and stripped.

        Returns:
            Regardless of whether extractor can be used or not, this returns the
            (extractor-specific) mapping value where each entry represents a semantic
            component that the extractor is looking for.
            If the value for an entry is None, the extractors generic matching code
            failed to find the relevant column.
            However, a specialized extractor class may override this class and leverage
            the existing mapping code while attempting to fill out still-unmatched
            parts.
        """
        pass

    @staticmethod
    def content_column_hdrs() -> List[str]:
        """Return prioritized list of column headers where extractor should
        extract the row's content.

        The content row is where the extractor will extract a brief (short
        documentation string) for the row and any sub-tables, if present.
        Also, if there is no dedicated column for row names, these too will be
        extracted from this column.

        Note:
            First match found in figure's actual table headers is used.

            This is intended to be overridden for specialized extractors where
            the content column is using a non-standard heading.
        """
        return ["description"]

    @staticmethod
    def label_column_hdrs() -> List[str]:
        """Return prioritized list of column headers where extractor should
        extract the row's name.

        Note:
            First match found in figure's actual table headers is used.

            This is intended to be overridden for specialized extractors where the label
            column is using a non-standard heading.
        """
        return ["attribute", "description"]
