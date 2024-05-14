# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Protocol

from spex.jsonspec.defs import JSON


class Code(Enum):
    O1000 = "general error"

    T1000 = (
        "error parsing table - the table's columns implied it should be parsed but "
        "some quirk of the table caused the parser to fail"
    )
    T1001 = "field overlaps with range of prior field"
    T1002 = "gap between this and the prior field"
    T1004 = "row order wrong, bits should be in desc order, bytes in asc order"
    T1006 = "non-standard table header"
    T1007 = "table skipped"
    T1008 = "failed to extract figure ID from table header"

    L1000 = "error extracting label"
    L1001 = "empty label"
    L1002 = "duplicate label"
    L1003 = "label missing, using imputed value"
    L1004 = "label contained invalid characters"
    L1007 = "label manually overridden"

    V1000 = "error extracting value"
    V1001 = "empty value"
    V1002 = "duplicate value"
    V1003 = "invalid value"

    R1000 = "error extracting range"
    R1001 = "invalid range, neither single offset value, nor a [high:low] range"
    R1002 = "range reversed"


class LintErr(Enum):
    ERR = Code.O1000

    TBL_PARSE_ERR = Code.T1000
    TBL_FIELD_OVERLAP = Code.T1001
    TBL_FIELD_GAP = Code.T1002
    TBL_ROW_ORDER_REVERSED = Code.T1004
    TBL_HDR_ERR = Code.T1006
    TBL_SKIPPED = Code.T1007
    TBL_FIG_ID_EXTRACT_ERR = Code.T1008

    LBL_EXTRACT_ERR = Code.L1000
    LBL_EMPTY = Code.L1001
    LBL_DUPLICATE = Code.L1002
    LBL_IMPUTED = Code.L1003
    LBL_INVALID_CHRS = Code.L1004
    LBL_OVERRIDDEN = Code.L1007

    VAL_EXTRACT_ERR = Code.V1000
    VAL_EMPTY = Code.V1001
    VAL_DUPLICATE = Code.V1002
    VAL_INVALID = Code.V1003

    RANGE_EXTRACT_ERR = Code.R1000
    RANGE_INVALID = Code.R1001
    RANGE_REVERSED = Code.R1002


@dataclass(frozen=True)
class LintEntry:
    err: LintErr
    fig: str
    msg: str = ""  # set later
    row: Optional[str] = None
    ctx: Dict[str, JSON] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.msg == "":
            object.__setattr__(self, "msg", self.err.value.value)
        assert (
            isinstance(self.fig, str) and self.fig != ""
        ), "invalid or empty figure value"
        assert isinstance(
            self.msg, str
        ), f"invalid msg, expected str, got {type(self.msg)}"
        assert isinstance(
            self.err, LintErr
        ), f"invalid code, expected {LintErr}, got {type(self.err)}"
        if self.err.value.name[0] in ("R", "L", "V"):
            assert self.row is not None, (
                "R|L|V codes point to a row or label/value within the row, "
                "row field must be set"
            )

    def to_json(self) -> JSON:
        ret: Dict[str, JSON] = {
            "code": self.err.value.name,
            "msg": self.msg,
            "fig": self.fig,
            "context": self.ctx,
        }
        if self.row is not None:
            ret["row"] = self.row
        return ret

    @property
    def code(self) -> str:
        return self.err.value.name


class Linter(Protocol):
    def add_issue(
        self,
        err: LintErr,
        fig: str,
        *,
        msg: Optional[str] = None,
        row_key: Optional[str] = None,
        ctx: Optional[Dict[str, JSON]] = None,
    ) -> None:
        ...

    def lint_entries(self) -> List[LintEntry]:
        ...
