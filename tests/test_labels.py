from typing import Callable, List

import pytest

from spex.jsonspec.defs import EntityMeta

from .utility import *  # noqa


@pytest.mark.xfail(
    reason="This will not succeed, it will be an acceptance test for the"
    "correctness of Spex"
)
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
                    "label": "TEST",
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


@pytest.mark.xfail(
    reason="This will not succeed, it will be an acceptance test for the"
    "correctness of Spex"
)
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
            "fields": [
                {
                    "val": "00b",
                    "label": "ter",
                }
            ],
        }
    ]


@pytest.mark.xfail(
    reason="This will not succeed, it will be an acceptance test for the"
    "correctness of Spex"
)
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


@pytest.mark.xfail(
    reason="This will not succeed, it will be an acceptance test for the"
    "correctness of Spex"
)
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
                    "brief": "This describes a brief, very brief.",
                }
            ],
        }
    ]
