# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterator,
    List,
    NotRequired,
    Protocol,
    TypeAlias,
    TypedDict,
    Union,
    cast,
    runtime_checkable,
)

if TYPE_CHECKING:
    from spex.jsonspec.extractors.figure import FigureExtractor
    from spex.xml import Element

JSON = Union[None, bool, str, float, int, List["JSON"], Dict[str, "JSON"]]


@runtime_checkable
class ToJson(Protocol):
    def to_json(self) -> JSON: ...


def cast_json(val: Any) -> JSON:
    """

    MyPy type-checker cannot determine that e.g. List[str] is a JSON value.
    Use this call to:
    1) satisfy type-checker
    2) clearly mark areas where this is an issue

    Args:
        val: supposedly JSON value

    Returns:
        same value, cast as a JSON value
    """
    return cast(JSON, val)


ExtractorMap: TypeAlias = Dict[str, "FigureExtractor"]
FigureId: TypeAlias = str
ValStr: TypeAlias = str

RESERVED = "RESERVED"
ELLIPSIS = "…"
OBSOLETE = "OBSOLETE"
NOTE = "NOTE"

SPECIAL_CASE_SET = {RESERVED, ELLIPSIS, OBSOLETE}


class ValueField(TypedDict):
    val: Union[str, int]
    label: str
    brief: NotRequired[str]


class ValueTable(TypedDict):
    title: NotRequired[str]
    parent_fig_id: NotRequired[str]
    fig_id: str
    fields: List[ValueField]


class Range(TypedDict):
    low: int | str
    high: int | str


MaybeRange = Union[Range, str]


class StructField(TypedDict):
    range: MaybeRange
    label: str
    brief: NotRequired[str]


class StructTable(TypedDict):
    title: NotRequired[str]
    parent_fig_id: NotRequired[str]
    fig_id: str
    fields: List[Union["StructTable", StructField]]


class EntityMeta(TypedDict):
    title: NotRequired[str]
    fig_id: str
    parent_fig_id: NotRequired[str]


class Entity(TypedDict):
    type: str
    title: NotRequired[str]
    fig_id: str
    parent_fig_id: NotRequired[str]
    fields: List[StructField] | List[ValueField]


class ParseFn(Protocol):
    def __call__(self, entity: EntityMeta, tbl: "Element") -> Iterator[Entity]: ...
