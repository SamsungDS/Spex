# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

"""
Code for iterating table rows while maintaining stable indexing into the row.

The various extractors overwhelmingly extract data (field names, description,
range/value) from specific columns.
This is complicated by two facts:
* A table cell may span multiple rows (the rowspan attribute). This means
  subsequent rows are missing an entry for the column at that offset, its
  existence is implied.
  * To make indexing easier, we store references to these rowspan cells, and
    re-insert them at their appropriate offset (see next point) for the
    following rows which the cell spans over.
* A table cell may span multiple columns (the colspan attribute). This means
  that looking up the nth element of a row can return different logical columns.
  * To consistently get the same logical column, we'd have to iterate over the
  cells, summing their colspan value (1 if omitted), returning the element
  corresponding to the requested offset.
"""
import copy
from typing import Iterator, List, Optional, Tuple

from lxml import etree

from spex.xml import Element, Xpath

ALST = Tuple[int, Tuple[Element, int]]


def repr_elem(elem: Element) -> str:
    return etree.tostring(elem, encoding="unicode").strip()


def alst_count_decr(alst: List[ALST]) -> List[ALST]:
    res = [(ndx, (elem, count - 1)) for ndx, (elem, count) in alst if count > 1]
    return res


def alst_insert(alst: List[ALST], ndx: int, elem: Element, count: int) -> None:
    entry = (ndx, (elem, count))
    for iter_ndx, (e_ndx, _) in enumerate(alst):
        if ndx < e_ndx:
            alst.insert(iter_ndx, entry)
            return
    alst.append(entry)


def sorted_row_children(row: Element, alst: List[ALST]) -> Iterator[Element]:
    elem_off: Optional[int]
    col_off = 0
    rest = alst
    (elem_off, (elem, _)), rest = rest[0], rest[1:]
    for td in Xpath.elems(row, "./td"):
        while elem_off is not None and elem_off == col_off:
            yield elem
            col_off += int(elem.get("colspan", 1))
            if rest:
                (elem_off, (elem, _)), rest = rest[0], rest[1:]
            else:
                elem_off = None

        yield td
        colspan = int(td.get("colspan", 1))
        col_off += colspan
    if elem_off is not None and elem_off == col_off:
        yield elem
    if rest:
        yield from (elem for (_, (elem, __)) in rest)


def alst_repr(alst: List[ALST]) -> str:
    return repr(
        [
            (ndx, (etree.tostring(elem, encoding="unicode").strip(), count))
            for (ndx, (elem, count)) in alst
        ]
    )


def row_iter(tbl: Element) -> Iterator[Element]:
    it = Xpath.elems(tbl, "./tr/td[1]/parent::tr")
    alst: List[ALST] = []

    row_cnt = 1
    for row in it:
        if alst:
            row_ = row
            # There's one or more cells to re-insert. Insert while respecting
            # the colspan's of every cell.
            row = etree.Element(row.tag)
            for key, val in row_.attrib.items():
                row.attrib[key] = val
            for td in sorted_row_children(row_, alst):
                # lxml elements can have _exactly_ one parent, this action
                # would re-parent the element, causing it to disappear from the
                # original XML tree.
                row.append(copy.deepcopy(td))

        # Find and store any cells with a rowspan attribute so that we can
        # re-insert these later.
        column_offset = 0
        for td in Xpath.elems(row, "./td"):
            row_span = int(td.get("rowspan", 1))
            if row_span > 1:
                elem = copy.copy(td)
                # avoid repeatedly processing this elem in subsequent rows
                del elem.attrib["rowspan"]
                alst_insert(alst, column_offset, elem, row_span)
            column_offset += int(td.get("colspan", 1))

        yield row

        alst = alst_count_decr(alst)
        row_cnt += 1


def get_cell_of(row: etree._Element, col: int) -> etree._Element:
    col_off = 0
    for td in Xpath.elems(row, "./td"):
        if col_off == col:
            return td
        col_off += int(td.get("colspan", 1))
    if col > col_off:
        raise IndexError(
            f"index out of range (requested {col} in row with columns [0;{col_off}])"
        )
    raise KeyError(f"requested {col}, no element starting at this index")
