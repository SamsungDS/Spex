from typing import Iterator, List
from spexs2.extractors.figure import FigureExtractor
from spexs2.defs import Entity
from xml import Element


class SkipTable(FigureExtractor):
    @classmethod
    def can_apply(cls, tbl_col_hdrs: List[str]) -> bool:
        raise RuntimeError("Don't add Skiptable to `extractors`, implied if no extractor can be applied.")

    def __call__(self) -> Iterator[Entity]:
        yield from ()
        return
