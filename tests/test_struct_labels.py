# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from typing import Callable, List

from spex.jsonspec.defs import EntityMeta

from .utility import *  # noqa


def test_label_bits_table_with_brief(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_doc: Callable[[str], str],
    html_table: Callable[[List[List[str]]], str],
):
    table = [
        ["Bits", "Description"],
        ["07:00", "This is the name(TEST): This describes a brief"],
    ]
    html = html_doc(html_table(table))

    json = html_parser(html, True)
    assert json == [
        {
            "title": "Figure 0: Test",
            "fig_id": "0",
            "type": "bits",
            "fields": [
                {
                    "range": {"low": 0, "high": 7},
                    "label": "test",
                    "brief": "This describes a brief",
                }
            ],
        }
    ]


def test_label_bytes_table_with_brief(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_doc: Callable[[str], str],
    html_table: Callable[[List[List[str]]], str],
):
    table = [
        ["Bytes", "Description"],
        ["07:00", "This is the name(TEST): This describes a brief, very brief."],
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
                    "label": "test",
                    "brief": "This describes a brief, very brief",
                }
            ],
        }
    ]


def test_label_bits_table_without_brief(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_doc: Callable[[str], str],
    html_table: Callable[[List[List[str]]], str],
):
    table = [
        ["Bits", "Description"],
        ["07:00", "This is the name(TEST)"],
    ]
    html = html_doc(html_table(table))

    json = html_parser(html, True)
    assert json == [
        {
            "title": "Figure 0: Test",
            "fig_id": "0",
            "type": "bits",
            "fields": [{"range": {"low": 0, "high": 7}, "label": "test"}],
        }
    ]


def test_label_bytes_table_without_brief(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_doc: Callable[[str], str],
    html_table: Callable[[List[List[str]]], str],
):
    table = [
        ["Bytes", "Description"],
        ["07:00", "This is the name(TEST)"],
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
                    "label": "test",
                }
            ],
        }
    ]
