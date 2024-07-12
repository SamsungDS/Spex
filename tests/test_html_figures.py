# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause
"""
Test the html to json parser by executing the parser on actual html examples
taken from the various NVMe specifications.

"""
from pathlib import Path
from typing import Callable, List

import pytest

from spex.jsonspec.defs import EntityMeta

from .utility import *  # noqa


def test_bits_fig37(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_loader: Callable[[str | Path], str],
):
    """Simple test case that simulates figure 37 from the
    NVM Express® Base Specification.

    This is the simplest bits table just containing a Bits and Description
    column.
    """
    html = html_loader("tests/resources/nvme_base_fig37.html")
    json_doc = html_parser(html, True)

    expected_json = [
        {
            "title": "Figure 37: Specification Version Descriptor",
            "fig_id": "37",
            "type": "bits",
            "fields": [
                {"range": {"low": 0, "high": 7}, "label": "ter"},
                {"range": {"low": 8, "high": 15}, "label": "mnr"},
                {"range": {"low": 16, "high": 31}, "label": "mjr"},
            ],
        }
    ]

    assert json_doc == expected_json


@pytest.mark.xfail(
    reason="This will not succeed, it will be an acceptance test for the"
    " correctness of Spex, something goes wrong in determining embedded table"
)
def test_bits_fig41(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_loader: Callable[[str | Path], str],
):
    """Simple test case that simulates figure 37 from the
    NVM Express® Base Specification.

    This is the simplest bits table just containing a Bits and Description
    column.
    """
    html = html_loader("tests/resources/nvme_base_fig41.html")
    json_doc = html_parser(html, True)


def test_bits_fig47(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_loader: Callable[[str | Path], str],
):
    """Test case that simulates figure 47 from the
    NVM Express® Base Specification.

    Test a bits table containing an extra column

    This table contains a bits and description header but also extra not
    necessary headers: Type & Reset.
    """
    html = html_loader("tests/resources/nvme_base_fig47.html")
    json_doc = html_parser(html, False)
    expected_json = [
        {
            "title": "Figure 47: Offset 38h: CMBLOC –"
            " Controller Memory Buffer Location",
            "fig_id": "47",
            "type": "bits",
            "fields": [
                {"range": {"low": 0, "high": 2}, "label": "bir"},
                {"range": {"low": 3, "high": 3}, "label": "cqmms"},
                {"range": {"low": 4, "high": 4}, "label": "cqpds"},
                {"range": {"low": 5, "high": 5}, "label": "cdpmls"},
                {"range": {"low": 6, "high": 6}, "label": "cdpcils"},
                {"range": {"low": 7, "high": 7}, "label": "cdmmms"},
                {
                    "range": {"low": 8, "high": 8},
                    "label": "cqda",
                    "brief": "If this bit is set to ‘1’, CDW11",
                },
                {"range": {"low": 9, "high": 11}, "label": "RESERVED"},
                {"range": {"low": 12, "high": 31}, "label": "ofst"},
            ],
        }
    ]

    assert json_doc == expected_json


def test_bytes_fig93(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_loader: Callable[[str | Path], str],
):
    """Simple test case that simulates figure 93 from the
    NVM Express® Base Specification.

    This table is the simplest bytes table. Containing only `Bytes` and
    `Description` columns.
    """
    html = html_loader("tests/resources/nvme_base_fig93.html")
    json_doc = html_parser(html, False)
    expected_rtrn = [
        {
            "title": "Figure 93: Common Command Format –"
            " Vendor Specific Commands (Optional)",
            "fig_id": "93",
            "type": "bytes",
            "fields": [
                {"range": {"low": 0, "high": 3}, "label": "cdw0"},
                {"range": {"low": 4, "high": 7}, "label": "nsid"},
                {"range": {"low": 8, "high": 39}, "label": "RESERVED"},
                {"range": {"low": 40, "high": 43}, "label": "ndt"},
                {"range": {"low": 44, "high": 47}, "label": "ndm"},
                {
                    "range": {"low": 48, "high": 51},
                    "label": "cdw12",
                    "brief": "This field is command specific Dword 12",
                },
                {
                    "range": {"low": 52, "high": 55},
                    "label": "cdw13",
                    "brief": "This field is command specific Dword 13",
                },
                {
                    "range": {"low": 56, "high": 59},
                    "label": "cdw14",
                    "brief": "This field is command specific Dword 14",
                },
                {
                    "range": {"low": 60, "high": 63},
                    "label": "cdw15",
                    "brief": "This field is command specific Dword 15",
                },
            ],
        }
    ]

    assert json_doc == expected_rtrn


def test_bytes_fig95(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_loader: Callable[[str | Path], str],
):
    """Advanced test case that simulates figure 94 from the
    NVM Express® Base Specification.

    This figure contains a byte table with a embedded bit table that contains
    yet another value table.

    Currently this won't succeed.
    """
    html = html_loader("tests/resources/nvme_base_fig95.html")
    json_doc = html_parser(html, False)


def test_bytes_fig94(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_loader: Callable[[str | Path], str],
):
    """Advanced test case that simulates figure 94 from the
    NVM Express® Base Specification.

    This figure contains a byte table with a embedded bit table that contains
    yet another value table.

    Currently this won't succeed.
    """
    html = html_loader("tests/resources/nvme_base_fig94.html")
    json_doc = html_parser(html, False)
    expected_rtrn = [
        {
            "fig_id": "94_4_0",
            "parent_fig_id": "94_4",
            "type": "values",
            "fields": [
                {"val": "00b", "label": "NO_DATA_IS_TRANSFERRED"},
                {
                    "val": "01b",
                    "label": "DATA_IS_TRANSFERRED_FROM_THE_HOST_TO_THE_CONTROLLER",
                },
                {
                    "val": "10b",
                    "label": "DATA_IS_TRANSFERRED_FROM_THE_CONTROLLER_TO_THE_HOST",
                },
                {"val": "11b", "label": "RESERVED"},
            ],
        },
        {
            "fig_id": "94_4",
            "parent_fig_id": "94",
            "type": "bits",
            "fields": [
                {"range": {"low": 0, "high": 1}, "label": "dtd"},
                {"range": {"low": 2, "high": 7}, "label": "f"},
            ],
        },
        {
            "title": "Figure 94: Fabrics Command – Submission\n"
            "                        Queue Entry Format",
            "fig_id": "94",
            "type": "bytes",
            "fields": [
                {
                    "range": {"low": 0, "high": 3},
                    "label": "cdw0",
                    "brief": "Refer to Figure 95",
                },
                {"range": {"low": 4, "high": 4}, "label": "fctype"},
                {"range": {"low": 5, "high": 23}, "label": "RESERVED"},
                {"range": {"low": 24, "high": 39}, "label": "sgl1"},
                {
                    "range": {"low": 40, "high": 63},
                    "label": "fcts",
                    "brief": "This field is Fabrics command type specific",
                },
            ],
        },
    ]

    assert json_doc == expected_rtrn


def test_values_fig101(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_loader: Callable[[str | Path], str],
):
    """Simple test case that simulates figure 101 from the
    NVM Express® Base Specification.

    This table is a simple table containing three columns with headers
    `Value`, `Description` and `References`.

    This is interesting because its the base case for values with an extra
    column compared to the value base case.
    """
    html = html_loader("tests/resources/nvme_base_fig101.html")
    json_doc = html_parser(html, False)
    expected_rtrn = [
        {
            "title": "Figure 101: Status Code – Status Code Type Values",
            "fig_id": "101",
            "type": "values",
            "fields": [
                {"val": "0h", "label": "GENERIC_COMMAND_STATUS"},
                {"val": "1h", "label": "COMMAND_SPECIFIC_STATUS"},
                {"val": "2h", "label": "MEDIA_AND_DATA_INTEGRITY_ERRORS"},
                {"val": "3h", "label": "PATH_RELATED_STATUS"},
                {"val": "4h to 6h", "label": "RESERVED"},
                {"val": "7h", "label": "VENDOR_SPECIFIC"},
            ],
        }
    ]

    assert json_doc == expected_rtrn


@pytest.mark.xfail(
    reason="This will not succeed, it will be an acceptance test for the"
    " correctness of Spex, currently its is missing support for dynamic tables"
)
def test_bytes_fig335(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_loader: Callable[[str | Path], str],
):
    """Advanced test case that simulates figure 335 from the
    NVM Express® Base Specification.

    This test case have a row mid table that denotes a second header.
    This second header is currently treated as a normal row. This
    is what we define as dynamic table or list table.
    """
    html = html_loader("tests/resources/nvme_base_fig335.html")
    json_doc = html_parser(html, True)
    assert json_doc == [
        {
            "title": "Figure 335: Ports List Data Structure",
            "fig_id": "335",
            "type": "bytes",
            "fields": [
                {"range": {"low": 0, "high": 7}, "label": "genctr"},
                {
                    "range": {"low": 8, "high": 15},
                    "label": "nument",
                    "brief": "Number of Fabrics Transport Entries in the Ports List",
                },
                {"range": {"low": 16, "high": 591}, "label": "fte1"},
                {
                    "range": {"low": 592, "high": 1167},
                    "label": "fte2",
                    "brief": "If any",
                },
                {
                    "range": {"low": -1, "high": -1},
                    "label": "…",
                },  # TODO: This should not be part of the output?
                {
                    "range": {"low": 576, "high": 576},
                    "label": "ften",
                    "brief": "If any",
                },
            ],
        }
    ]


def test_bytes_fig559(
    html_parser: Callable[[str, bool], List[EntityMeta]],
    html_loader: Callable[[str | Path], str],
):
    """Test case that simulates figure 559 from the
    NVM Express® Base Specification.

    This test case contains a bits table, that contains an embedded value table.
    It fails because of the `Definition` header.
    """
    html = html_loader("tests/resources/nvme_base_fig559.html")
    json_doc = html_parser(html, False)
    assert json_doc == [
        {
            "fig_id": "559_0",
            "parent_fig_id": "559",
            "type": "values",
            "fields": [
                {"val": "00h", "label": "NO_ACTION"},
                {"val": "01h", "label": "RECLAIM_UNIT_HANDLE_STATUS"},
                {"val": "ffh", "label": "VENDOR_SPECIFIC"},
                {"val": "all others", "label": "RESERVED"},
            ],
        },
        {
            "title": "Figure 559: I/O Management Receive – Command Dword 10",
            "fig_id": "559",
            "type": "bits",
            "fields": [
                {"range": {"low": 0, "high": 7}, "label": "mo"},
                {"range": {"low": 8, "high": 15}, "label": "RESERVED"},
                {"range": {"low": 16, "high": 31}, "label": "mos"},
            ],
        },
    ]
