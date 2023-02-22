from typing import TYPE_CHECKING
from spexs2.document import DocumentParser
from spexs2.extractors.structtable import StructTableExtractor
from spexs2.xml import Xpath


if TYPE_CHECKING:
    from spexs2.xml import Element


class ZndFig48(StructTableExtractor):
    type = "bytes"

    def data_extract(self, row: "Element") -> "Element":
        return Xpath.elem_first_req(row, "./td[3]")


class ZndFig50(StructTableExtractor):
    type = "bytes"

    def data_extract(self, row: "Element") -> "Element":
        return Xpath.elem_first_req(row, "./td[3]")


class NvmCsZoned11c(DocumentParser):

    label_overrides = {
        ("37", "0"): "zt",
        ("37", "1"): "zs",
        ("37", "2"): "za",
    }

    fig_extractor_overrides = {
        "48": ZndFig48,
        "50": ZndFig50,
    }
