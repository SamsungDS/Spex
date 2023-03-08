from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Protocol
from spexs2.defs import JSON, ToJson


class Code(Enum):
    O1000 = "general error"

    T1000 = "error parsing table"
    T1001 = "field overlaps with range of prior field"
    T1002 = "gap between this and the prior field"
    T1003 = "duplicate field name"
    T1004 = "row order wrong, bits should be in desc order, bytes in asc order"
    T1005 = "duplicate value"
    T1006 = "non-standard table header"

    R1000 = "error parsing row"

    L1000 = "error extracting label"
    L1001 = "empty label"
    L1002 = "duplicate label"
    L1003 = "cannot infer label"
    L1004 = "label contained invalid characters"
    L1005 = "label cannot start with a number"
    L1006 = "missing field name"

    V1000 = "error extracting value"
    V1001 = "empty value"
    V1002 = "cannot parse value as range ([high:low])"
    V1003 = "range reversed"


@dataclass(frozen=True)
class LintEntry:
    code: Code
    fig: str
    msg: str = ""  # set later
    row: Optional[str] = None
    ctx: Dict[str, JSON] = field(default_factory=dict)

    def __post_init__(self):
        if self.msg == "":
            object.__setattr__(self, "msg", self.code.value)
            if self.code.name[1:] == "1000":
                raise RuntimeError("cannot raise generic error ('<X>1000') without a description")
        assert isinstance(self.fig, str) and self.fig != "", "invalid or empty figure value"
        assert isinstance(self.msg, str), f"invalid msg, expected str, got {type(self.msg)}"
        assert isinstance(self.code, Code), f"invalid code, expected {Code}, got {type(self.code)}"
        if self.code.name[0] in ("R", "L", "V"):
            assert self.row is not None, "R|L|V codes point to a row or label/value within the row, row field must be set"

    def to_json(self) -> JSON:
        ret: Dict[str, JSON] = {"code": self.code.name, "msg": self.msg, "fig": self.fig, "context": self.ctx}
        if self.row is not None:
            ret["row"] = self.row
        return ret


class Linter(Protocol):
    def add_issue(self, c: Code, fig: str, *,
                  msg: Optional[str] = None,
                  row: Optional[str] = None,
                  ctx: Optional[Dict[str, JSON]] = None) -> LintEntry: ...
