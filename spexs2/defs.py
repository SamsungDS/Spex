from typing import TYPE_CHECKING, Dict, Iterator, TypedDict, NotRequired, Protocol, List, Union

if TYPE_CHECKING:
    from spexs2.extractors.figure import FigureExtractor
    from spexs2.xml import Element


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


class ValueField(TypedDict):
    val: str
    label: str
    brief: NotRequired[str]


class ValueTable(TypedDict):
    title: NotRequired[str]
    parent_fig_id: NotRequired[str]
    fig_id: str
    fields: List[ValueField]


class Range(TypedDict):
    start: int
    end: int


class StructField(TypedDict):
    range: Union[Range, str]
    label: str
    brief: NotRequired[str]


class StructTable(TypedDict):
    title: NotRequired[str]
    parent_fig_id: NotRequired[str]
    fig_id: str
    fields: List[Union["StructTable", StructField]]
