from typing import Iterator, Tuple, Optional
from spexs2.document import DocumentParser
from spexs2.extractors.figure import RowResult
from spexs2.extractors.structtable import StructTableExtractor
from spexs2.defs import Entity
from spexs2.xml import Element, Xpath


class NvmFig23(StructTableExtractor):
    type = "bits"
    _fig24: Optional[Element]

    def __post_init__(self) -> None:
        self._fig24 = None

    def rows_on_err(self, row: Element, err: Exception) -> Optional[RowResult]:
        try:
            return super().rows_on_err(row, err)
        except StopIteration as e:
            raise e
        except Exception as e:
            row_txt = "".join(
                e.decode("utf-8") if isinstance(e, bytes) else e
                for e in row.itertext()).lstrip().lower()
            if row_txt.startswith("figure 24"):
                self._fig24 = row
            raise StopIteration  # stop further processing

    def __call__(self) -> Iterator["Entity"]:
        yield from super().__call__()
        # TODO: what to do, gotta emit fig24 also..
        # can I create a new tbl object and yield it..? as a subtbl ?
        assert self._fig24 is not None, "did not find fig24...!?"
        # yield from self.__parse(self._fig24)


class NvmFig97(StructTableExtractor):
    type = "bytes"

    def data_extract(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, "./td[3]")


class NvmFig100(StructTableExtractor):
    type = "bytes"

    def data_extract(self, row: "Element") -> "Element":
        return Xpath.elem_first_req(row, "./td[3]")


class NvmCmdSet1c(DocumentParser):
    fig_extractor_overrides = {
        "23": NvmFig23,
        "97": NvmFig97,
        "100": NvmFig100,
    }
