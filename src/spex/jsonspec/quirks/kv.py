# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from typing import Generator, Iterator, List

from spex.jsonspec.defs import Entity, StructField
from spex.jsonspec.document import DocumentParser
from spex.jsonspec.extractors.figure import RowErrPolicy
from spex.jsonspec.extractors.structtable import BytesTableExtractor
from spex.xml import Element, XmlUtils


class KvFig41(BytesTableExtractor):
    def row_err_handler(
        self,
        row_it: Iterator[Element],
        row: Element,
        fields: List[StructField],
        err: Exception,
    ) -> Generator["Entity", None, RowErrPolicy]:
        # Figure has a row spanning all columns with a comment which we can ignore
        yield from ()
        row_txt = XmlUtils.to_text(row)
        if not row_txt.endswith("(refer to Figure 39)."):
            return RowErrPolicy.Raise
        return RowErrPolicy.Continue


class NvmKv1_0c(DocumentParser):
    label_overrides = {}

    fig_extractor_overrides = {
        "41": KvFig41,
    }
