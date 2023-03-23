from lxml import etree
from spex.xml import Xpath, XmlUtils
from spex.model.rowiter import row_iter
import pytest


def tree_lead_rspan2():
    """table where first row's first cell spans 2 rows."""
    return etree.fromstring(
        """
    <table>
      <tr>
        <td rowspan="2">rspan2</td>
        <td>r1</td>
      </tr>
      <tr>
        <td>r2</td>
      </tr>
    </table>"""
    )


def tree_middle_rspan2():
    return etree.fromstring(
        """
    <table>
    <tr>
      <td>r1d1</td>
      <td>r1d2</td>
    </tr>
    <tr>
      <td>r2d1</td>
      <td rowspan="2">rspan2</td>
    </tr>
    <tr>
      <td>r3d1</td>
    </tr>
    <tr>
      <td>r4d1</td>
      <td>r4d2</td>
    </tr>
    </table>
    """
    )


def tree_rspan_colspan():
    return etree.fromstring(
        """
    <table>
    <tr>
      <td colspan="2">r1d1</td>
      <td rowspan="3">rspan1</td>
      <td>r1d3</td>
    </tr>
    <tr>
      <td colspan="2">r2d1</td>
      <td rowspan="2">rspan2</td>
    </tr>
    <tr>
      <td>r3d1</td>
      <td>r3d2</td>
    </tr>
    </table>"""
    )


def tbl_rowlens(tbl):
    """Count number of td (column) elems in each tr (row)."""
    return [len(Xpath.elems(tr, "./td")) for tr in Xpath.elems(tbl, "./tr")]


@pytest.mark.parametrize(
    "tbl, rowlens, row_iter_lens",
    [
        (tree_lead_rspan2(), [2, 1], [2, 2]),
        (tree_middle_rspan2(), [2, 2, 1, 2], [2, 2, 2, 2]),
        (tree_rspan_colspan(), [3, 2, 2], [3, 3, 4]),
    ],
)
def test_row_lengths(tbl, rowlens, row_iter_lens):
    """
    `row_iter` should re-insert td's spanning multiple rows into subsequent
    rows. This test only checks row lengths reflect that this should have been
    done - it does NOT check td contents or ordering.
    """
    assert len(rowlens) == len(
        row_iter_lens
    ), "error in test, must expect a certain number of rows"
    assert rowlens == tbl_rowlens(tbl)
    assert row_iter_lens == [len(r) for r in row_iter(tbl)]


@pytest.mark.parametrize(
    "tbl, tbl_txts_expected",
    [
        (tree_lead_rspan2(), [["rspan2", "r1"], ["rspan2", "r2"]]),
        (
            tree_middle_rspan2(),
            [
                ["r1d1", "r1d2"],
                ["r2d1", "rspan2"],
                ["r3d1", "rspan2"],
                ["r4d1", "r4d2"],
            ],
        ),
        (
            tree_rspan_colspan(),
            [
                ["r1d1", "rspan1", "r1d3"],
                ["r2d1", "rspan1", "rspan2"],
                ["r3d1", "r3d2", "rspan1", "rspan2"],
            ],
        ),
    ],
)
def test_row_contents(tbl, tbl_txts_expected):
    tbl_txts = []
    for row in row_iter(tbl):
        row_txts = []
        for td in Xpath.elems(row, "./td"):
            row_txts.append(XmlUtils.to_text(td))
        tbl_txts.append(row_txts)
    assert tbl_txts == tbl_txts_expected
