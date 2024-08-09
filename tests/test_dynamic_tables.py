# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path
from typing import Callable, List

from spex.jsonspec.defs import EntityMeta

from .utility import *  # noqa


def test_simple_dynamic_table(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_loader: Callable[[str | Path], str],
) -> None:
    html = html_loader("tests/resources/dynamic_table.html")
    json = html_parser(html, True)
    assert json == [
        {
            "title": "Figure 1: Test",
            "fig_id": "1",
            "type": "bytes",
            "fields": [
                {
                    "label": "testctr",
                    "range": {"low": 0, "high": 7},
                    "brief": "This field indicates a test counter",
                },
                {
                    "label": "te1",
                    "range": {"low": "8", "high": "583"},
                    "brief": "The first Test\n"
                    "                        Entry data structure",
                },
                {
                    "label": "te2",
                    "range": {"low": "584", "high": "1159"},
                    "brief": "If any",
                },
                {
                    "label": "tet",
                    "range": {"low": "576*(TESTCTR-1)+8", "high": "576*TESTCTR+7"},
                    "brief": "If any",
                },
            ],
        }
    ]
