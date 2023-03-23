from typing import Iterator, List
from spex.model.extractors.figure import FigureExtractor
from spex.model.defs import Entity


class SkipTable(FigureExtractor):
    @classmethod
    def can_apply(cls, tbl_col_hdrs: List[str]) -> bool:
        raise RuntimeError(
            "Don't add Skiptable to `extractors`, implied if no extractor can be applied."
        )

    def __call__(self) -> Iterator[Entity]:
        yield from ()
        return
