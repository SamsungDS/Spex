import dataclasses as dc
from enum import Enum

from lxml.etree import _Element

from spex.xml import Xpath


class VMerge(Enum):
    NONE = 0
    MERGED = 1
    RESTART = 2


@dc.dataclass()
class GridElement:
    cell: _Element
    top: int
    bottom: int
    left: int
    right: int

    @property
    def colspan(self) -> int:
        return self.right - self.left + 1

    @property
    def rowspan(self) -> int:
        return self.bottom - self.top + 1


class TableWrap:
    def __init__(self, elem: _Element):
        self._elem = elem

    def grid(self):
        def tc_grid_span(tc: _Element) -> int:
            ret = Xpath.attr_first(tc, "./w:tcPr/w:gridSpan/@w:val")
            return int(ret) if isinstance(ret, str) else 1

        def tc_vmerge(tc: _Element) -> VMerge:
            vmerge_elem = Xpath.elem_first(tc, "./w:tcPr/w:vMerge")
            if vmerge_elem is None:
                return VMerge.NONE
            assert isinstance(vmerge_elem, _Element)
            rval = Xpath.attr_first(vmerge_elem, "@w:val")
            if rval:
                assert rval == "restart"
                return VMerge.RESTART
            else:
                return VMerge.MERGED

        matrix = []
        for rndx, tr in enumerate(Xpath.elems(self._elem, "./w:tr")):
            cndx = 0
            mrow = []
            for tc in tr.findall("./w:tc", tr.nsmap):
                grid_span = tc_grid_span(tc)
                vmerge = tc_vmerge(tc)
                if vmerge is VMerge.MERGED:
                    lcell = matrix[-1][cndx]
                    assert (
                        grid_span == lcell.colspan
                    ), f"cell has grid_span {grid_span}, but parent has {lcell.colspan} - breaks assumption of rectangular-only merges"
                    # update bottom value to mark
                    lcell.bottom = rndx
                else:
                    # create layout cell, bottom value is asssumed if vMerge="restart"
                    # in that case, subsequent cells which are merged into this will
                    # update the bottom value accordingly.
                    lcell = GridElement(
                        top=rndx,
                        bottom=rndx,
                        left=cndx,
                        right=cndx + grid_span - 1,
                        cell=tc,
                    )

                for _ in range(grid_span):
                    mrow.append(lcell)
                cndx += grid_span
            matrix.append(mrow)
        return matrix
