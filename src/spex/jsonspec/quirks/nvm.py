# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from typing import Generator, Iterator, List, Optional

from lxml import etree

from spex.jsonspec.defs import Entity, EntityMeta, StructField
from spex.jsonspec.document import DocumentParser
from spex.jsonspec.extractors.figure import RowErrPolicy
from spex.jsonspec.extractors.skiptable import SkipTable
from spex.jsonspec.extractors.structtable import BitsTableExtractor, BytesTableExtractor
from spex.xml import Element


class NvmFig23(BitsTableExtractor):
    _fig24_meta: Optional[EntityMeta]
    _fig24: Optional[Element]

    def __post_init__(self) -> None:
        self._fig24_meta = None
        self._fig24 = None

    def row_err_handler(
        self,
        row_it: Iterator[Element],
        row: Element,
        fields: List[StructField],
        err: Exception,
    ) -> Generator["Entity", None, RowErrPolicy]:
        # TODO: raise lint error

        # Figure 24 is unfortunately part of Figure 23 in the original Docx
        # file (and thus the resulting HTML).
        # The row error handler is triggered when we encounter the row containing
        # the title for figure 24.
        # From there, we construct a table and meta element, save both and override
        # the normal __call__ implementation to first process the (figure 23) struct
        # table as usual, then yield Figure 24.
        row_txt = (
            "".join(
                elem.decode("utf-8") if isinstance(elem, bytes) else elem
                for elem in row.itertext()
            )
            .lstrip()
            .lower()
        )
        if not row_txt.startswith("figure 24"):
            return RowErrPolicy.Raise

        f24_tbl = etree.Element("table")
        for f24_row in row.itersiblings():
            f24_tbl.append(f24_row)
        entity_meta: EntityMeta = {"fig_id": "24"}
        title = self.doc_parser._on_extract_figure_title(row)
        if isinstance(title, str):
            entity_meta["title"] = title

        # Don't yield now, then the table would come before Fig 23
        # instead, save the element, yield after fig 23's __call__ finishes
        self._fig24_meta = entity_meta
        self._fig24 = f24_tbl
        yield from ()
        return RowErrPolicy.Stop

    def __call__(self) -> Iterator[Entity]:
        yield from super().__call__()
        if self._fig24_meta is not None and self._fig24 is not None:
            yield from self._parse(self._fig24_meta, self._fig24)


# class NvmFig97(BytesTableExtractor):
#     def data_extract(self, row: Element) -> Element:
#         return Xpath.elem_first_req(row, "./td[3]")
#
#
# class NvmFig100(BytesTableExtractor):
#     def data_extract(self, row: "Element") -> "Element":
#         return Xpath.elem_first_req(row, "./td[3]")


class NvmFig41(BytesTableExtractor):
    @staticmethod
    def content_column_hdrs() -> List[str]:
        return ["field"]

    @staticmethod
    def label_column_hdrs() -> List[str]:
        return ["field"]


class NvmCmdSet1c(DocumentParser):
    label_overrides = {
        ("42_4", "00b"): "none",
        ("42_4", "01b"): "idle",
        ("42_4", "10b"): "normal",
        ("42_4", "11b"): "low",
        ("49_0_4", "00b"): "none",
        ("42_0_4", "01b"): "idle",
        ("49_0_4", "10b"): "normal",
        ("49_0_4", "11b"): "low",
        ("64_0_4", "00b"): "none",
        ("64_0_4", "01b"): "idle",
        ("64_0_4", "10b"): "normal",
        ("64_0_4", "11b"): "low",
    }
    fig_extractor_overrides = {
        "23": NvmFig23,
        "41": SkipTable,
        # "97": NvmFig97,  # TODO: should be inferred
        # "100": NvmFig100,  # TODO: should be inferred
    }
