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
