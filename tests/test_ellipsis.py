# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause


from typing import Callable, List

from spex.jsonspec.defs import EntityMeta

from .utility import *  # noqa


def test_basic_ellipsis_single_column(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_doc: Callable[[str], str],
    html_table: Callable[[List[List[str]]], str],
):
    table = [["Value", "Description"], ["00b", "VALUE1"], ["…"], ["01b", "VALUE2"]]
    html = html_doc(html_table(table))

    json = html_parser(html, True)
    assert json == [
        {
            "title": "Figure 0: Test",
            "fig_id": "0",
            "type": "values",
            "fields": [
                {"val": "00b", "label": "VALUE1"},
                {"val": "…", "label": "…"},
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
        ["…", " … "],
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
                {"val": "…", "label": "…"},
                {"val": "01b", "label": "VALUE2"},
            ],
        }
    ]


def test_struct_basic_ellipsis_all_column(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_doc: Callable[[str], str],
    html_table: Callable[[List[List[str]]], str],
):
    table = [
        ["Bytes", "Description"],
        ["07:00", "This is the name(TEST1): This describes a brief, very brief."],
        ["…", " … "],
        ["10:08", "This is the name(TEST2): This describes a brief, very brief."],
    ]
    html = html_doc(html_table(table))

    json = html_parser(html, True)
    assert json == [
        {
            "title": "Figure 0: Test",
            "fig_id": "0",
            "type": "bytes",
            "fields": [
                {
                    "range": {"low": 0, "high": 7},
                    "label": "test1",
                    "brief": "This describes a brief, very brief",
                },
                {
                    "range": {"low": 8, "high": 10},
                    "label": "test2",
                    "brief": "This describes a brief, very brief",
                },
            ],
        }
    ]


def test_struct_basic_ellipsis_single_column(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_doc: Callable[[str], str],
    html_table: Callable[[List[List[str]]], str],
):
    table = [
        ["Bytes", "Description"],
        ["07:00", "This is the name(TEST1): This describes a brief, very brief."],
        ["…"],
        ["10:08", "This is the name(TEST2): This describes a brief, very brief."],
    ]
    html = html_doc(html_table(table))

    json = html_parser(html, True)
    assert json == [
        {
            "title": "Figure 0: Test",
            "fig_id": "0",
            "type": "bytes",
            "fields": [
                {
                    "range": {"low": 0, "high": 7},
                    "label": "test1",
                    "brief": "This describes a brief, very brief",
                },
                {"range": {"low": -1, "high": -1}, "label": "…"},
                {
                    "range": {"low": 8, "high": 10},
                    "label": "test2",
                    "brief": "This describes a brief, very brief",
                },
            ],
        }
    ]
