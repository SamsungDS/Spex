from typing import TYPE_CHECKING, Dict, Iterator, TypedDict, NotRequired, Protocol, List, Union, runtime_checkable


if TYPE_CHECKING:
    from spex.model.xml import Element
    from spex.model.extractors.figure import FigureExtractor


JSON = Union[None, bool, str, float, int, List['JSON'], Dict[str, 'JSON']]


@runtime_checkable
class ToJson(Protocol):
    def to_json(self) -> JSON: ...


class EntityMeta(TypedDict):
    title: NotRequired[str]
    fig_id: str
    parent_fig_id: NotRequired[str]


class Entity(TypedDict):
    type: str
    title: NotRequired[str]
    fig_id: str
    parent_fig_id: NotRequired[str]
    data: dict


class ParseFn(Protocol):
    def __call__(self, entity: EntityMeta, tbl: "Element") -> Iterator[Entity]: ...


ExtractorMap = Dict[str, "FigureExtractor"]
FigureId = str
ValStr = str

RESERVED = "RESERVED"
ELLIPSIS = "…"


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
    low: int
    high: int


class StructField(TypedDict):
    range: Union[Range, str]
    label: str
    brief: NotRequired[str]


class StructTable(TypedDict):
    title: NotRequired[str]
    parent_fig_id: NotRequired[str]
    fig_id: str
    fields: List[Union["StructTable", StructField]]
