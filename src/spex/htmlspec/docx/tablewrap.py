# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass
from enum import Enum
from typing import List

from lxml.etree import _Element

from spex.xml import Xpath


class VerticalMergeState(Enum):
    NONE = 0
    MERGED = 1
    RESTART = 2


@dataclass()
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


Matrix = List[List[GridElement]]


class TableWrap:
    def __init__(self, elem: _Element):
        self._elem = elem

    def grid(self) -> Matrix:
        def tc_grid_span(tc: _Element) -> int:
            ret = Xpath.attr_first(tc, "./w:tcPr/w:gridSpan/@w:val")
            return int(ret) if isinstance(ret, str) else 1

        def cell_vertical_merge(tc: _Element) -> VerticalMergeState:
            merge_elem = Xpath.elem_first(tc, "./w:tcPr/w:vMerge")
            if merge_elem is None:
                return VerticalMergeState.NONE
            assert isinstance(merge_elem, _Element)
            row_val = Xpath.attr_first(merge_elem, "@w:val")
            if row_val:
                assert row_val == "restart"
                return VerticalMergeState.RESTART
            else:
                return VerticalMergeState.MERGED

        matrix: Matrix = []
        for row_index, row in enumerate(Xpath.elems(self._elem, "./w:tr")):
            cell_index = 0
            merge_row = []
            for cell in row.findall("./w:tc", row.nsmap):  # type: ignore
                grid_span = tc_grid_span(cell)
                vertical_merge = cell_vertical_merge(cell)
                if vertical_merge is VerticalMergeState.MERGED:
                    left_cell = matrix[-1][cell_index]
                    assert grid_span == left_cell.colspan, (
                        f"cell has grid_span {grid_span}, but parent has "
                        f"{left_cell.colspan} - breaks assumption of "
                        "rectangular-only merges"
                    )
                    # update bottom value to mark
                    left_cell.bottom = row_index
                else:
                    # create layout cell, bottom value is asssumed if vMerge="restart"
                    # in that case, subsequent cells which are merged into this will
                    # update the bottom value accordingly.
                    left_cell = GridElement(
                        top=row_index,
                        bottom=row_index,
                        left=cell_index,
                        right=cell_index + grid_span - 1,
                        cell=cell,
                    )

                for _ in range(grid_span):
                    merge_row.append(left_cell)
                cell_index += grid_span
            matrix.append(merge_row)
        return matrix
