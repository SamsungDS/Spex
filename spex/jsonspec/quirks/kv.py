from typing import Iterator, List, Generator

from spex.jsonspec.defs import StructField
from spex.jsonspec.extractors.figure import RowErrPolicy
from spex.jsonspec.document import DocumentParser
from spex.jsonspec.extractors.structtable import BytesTableExtractor
from spex.xml import Element, XmlUtils


class KvFig41(BytesTableExtractor):

    def row_err_handler(self, row_it: Iterator[Element], row: Element, fields: List[StructField], err: Exception) -> \
    Generator["Entity", None, RowErrPolicy]:
        # Figure has a row spanning all columns with a comment which we can ignore
        yield from ()
        row_txt = XmlUtils.to_text(row)
        if not row_txt.endswith("(refer to Figure 39)."):
            return RowErrPolicy.Raise
        return RowErrPolicy.Continue


class NvmKv1_0c(DocumentParser):
    label_overrides = {
    }

    fig_extractor_overrides = {
        "41": KvFig41,
    }
