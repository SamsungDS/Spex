from typing import Callable, List

from spex.jsonspec.defs import EntityMeta

from .utility import *  # noqa


def test_basic_ellipsis_single_column(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_doc: Callable[[str], str],
    html_table: Callable[[List[List[str]]], str],
):
    table = [["Value", "Description"], ["00b", "VALUE1"], ["..."], ["01b", "VALUE2"]]
    html = html_doc(html_table(table))

    json = html_parser(html, True)
    assert json == [
        {
            "title": "Figure 0: Test",
            "fig_id": "0",
            "type": "values",
            "fields": [
                {"val": "00b", "label": "VALUE1"},
                {"val": "01b", "label": "VALUE2"},
            ],
        }
    ]


def test_basic_ellipsis_all_column(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_doc: Callable[[str], str],
    html_table: Callable[[List[List[str]]], str],
):
    table = [
        ["Value", "Description"],
        ["00b", "VALUE1"],
        ["...  ", " ... "],
        ["01b", "VALUE2"],
    ]
    html = html_doc(html_table(table))

    json = html_parser(html, True)
    assert json == [
        {
            "title": "Figure 0: Test",
            "fig_id": "0",
            "type": "values",
            "fields": [
                {"val": "00b", "label": "VALUE1"},
                {"val": "...", "label": "..."},
                {"val": "01b", "label": "VALUE2"},
            ],
        }
    ]
