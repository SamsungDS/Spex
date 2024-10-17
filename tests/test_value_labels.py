# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from typing import Callable, List

from spex.jsonspec.defs import EntityMeta

from .utility import *  # noqa


def test_label_value_table_with_brief(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_doc: Callable[[str], str],
    html_table: Callable[[List[List[str]]], str],
):
    table = [
        ["Value", "Description"],
        ["00b", "This is the name(Test): This describes a brief"],
    ]
    html = html_doc(html_table(table))

    json = html_parser(html, True)
    assert json == [
        {
            "title": "Figure 0: Test",
            "fig_id": "0",
            "type": "values",
            "fields": [
                {
                    "val": "00b",
                    "label": "THIS_IS_THE_NAME",
                    "brief": "This describes a brief",
                }
            ],
        }
    ]


def test_label_value_table_without_acronym(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_doc: Callable[[str], str],
    html_table: Callable[[List[List[str]]], str],
):
    table = [
        ["Value", "Description"],
        ["00b", "This is the name: Lorem ipsum dolor sit amet"],
    ]
    html = html_doc(html_table(table))

    json = html_parser(html, True)
    assert json == [
        {
            "title": "Figure 0: Test",
            "fig_id": "0",
            "type": "values",
            "fields": [
                {
                    "val": "00b",
                    "label": "THIS_IS_THE_NAME",
                    "brief": "Lorem ipsum dolor sit amet",
                }
            ],
        }
    ]


def test_label_value_table_without_brief(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_doc: Callable[[str], str],
    html_table: Callable[[List[List[str]]], str],
):
    table = [
        ["Value", "Description"],
        ["00b", "Tertiary Version (TER)"],
    ]
    html = html_doc(html_table(table))

    json = html_parser(html, True)
    assert json == [
        {
            "title": "Figure 0: Test",
            "fig_id": "0",
            "type": "values",
            "fields": [{"val": "00b", "label": "TERTIARY_VERSION"}],
        }
    ]


def test_label_value_table_with_num_prefix(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_doc: Callable[[str], str],
    html_table: Callable[[List[List[str]]], str],
):
    table = [
        ["Value", "Definition"],
        ["0h", "1 microsecond"],
        ["1h", "10 microseconds"],
        ["2h", "100 microseconds"],
        ["3h", "1 millisecond"],
        ["4h", "10 milliseconds"],
        ["5h", "100 milliseconds"],
        ["6h", "1 second"],
        ["7h", "10 seconds"],
        ["8h", "100 seconds"],
        ["9h", "1,000 seconds"],
        ["Ah", "10,000 seconds"],
        ["Bh", "100,000 seconds"],
        ["Ch", "1,000,000 seconds"],
        ["Dh", "Reserved"],
        ["Eh", "Reserved"],
        ["Fh", "Reserved"],
    ]
    html = html_doc(html_table(table))

    json = html_parser(html, False)
    assert json == [
        {
            "title": "Figure 0: Test",
            "fig_id": "0",
            "fields": [
                {"val": "0h", "label": "MICROSECOND_1"},
                {"val": "1h", "label": "MICROSECONDS_10"},
                {"val": "2h", "label": "MICROSECONDS_100"},
                {"val": "3h", "label": "MILLISECOND_1"},
                {"val": "4h", "label": "MILLISECONDS_10"},
                {"val": "5h", "label": "MILLISECONDS_100"},
                {"val": "6h", "label": "SECOND_1"},
                {"val": "7h", "label": "SECONDS_10"},
                {"val": "8h", "label": "SECONDS_100"},
                {"val": "9h", "label": "1"},
                {"val": "ah", "label": "10"},
                {"val": "bh", "label": "100"},
                {"val": "ch", "label": "1"},
                {"val": "dh", "label": "RESERVED"},
                {"val": "eh", "label": "RESERVED"},
                {"val": "fh", "label": "RESERVED"},
            ],
            "type": "values",
        }
    ]
