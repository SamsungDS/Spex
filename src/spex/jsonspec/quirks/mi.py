# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from typing import Generator, Iterator, List, Optional

from lxml import etree

from spex.jsonspec.defs import Entity, EntityMeta, StructField
from spex.jsonspec.document import DocumentParser
from spex.jsonspec.extractors.figure import RowErrPolicy
from spex.jsonspec.extractors.structtable import BitsTableExtractor
from spex.xml import Element


class MiFig64(BitsTableExtractor):
    _extra_fig_meta: Optional[EntityMeta]
    _extra_fig: Optional[Element]

    def __post_init__(self) -> None:
        self._extra_fig_meta = None
        self._extra_fig = None

    def row_err_handler(
        self,
        row_it: Iterator[Element],
        row: Element,
        fields: List[StructField],
        err: Exception,
    ) -> Generator["Entity", None, RowErrPolicy]:
        # TODO: raise lint error

        row_txt = (
            "".join(
                elem.decode("utf-8") if isinstance(elem, bytes) else elem
                for elem in row.itertext()
            )
            .lstrip()
            .lower()
        )
        if not row_txt.startswith("figure 65"):
            return RowErrPolicy.Raise

        extra_fig = etree.Element("table")
        for extra_fig_row in row.itersiblings():
            extra_fig.append(extra_fig_row)
        entity_meta: EntityMeta = {"fig_id": "65"}
        title = self.doc_parser._on_extract_figure_title(row)
        if isinstance(title, str):
            entity_meta["title"] = title

        # Don't yield now, then the extra table would precede the first table.
        # Instead, save the table, yield after finishing the parsing of this table
        self._extra_fig_meta = entity_meta
        self._extra_fig = extra_fig
        yield from ()
        return RowErrPolicy.Stop

    def __call__(self) -> Iterator[Entity]:
        yield from super().__call__()
        if self._extra_fig_meta is not None and self._extra_fig is not None:
            yield from self._parse(self._extra_fig_meta, self._extra_fig)


class NvmMi1_2c(DocumentParser):
    label_overrides = {
        ("19", "2"): "misc",
    }

    fig_extractor_overrides = {
        "64": MiFig64,
    }
