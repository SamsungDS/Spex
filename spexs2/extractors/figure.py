from typing import TYPE_CHECKING, Optional, Iterator
from spexs2.xml import Element, Xpath
from spexs2 import xml  # TODO: for debugging


if TYPE_CHECKING:
    from spexs2.defs import EntityMeta, ParseFn, Entity
    from spexs2.document import DocumentParser


class FigureExtractor:
    BRIEF_MAXLEN: int = 60

    def __init__(self,
                 doc_parser: "DocumentParser",
                 entity_meta: "EntityMeta",
                 tbl: Element,
                 parse_fn: "ParseFn"):
        self.doc_parser = doc_parser
        self.__entity_meta = entity_meta
        self.__tbl = tbl
        self.__parse = parse_fn
        self.__post_init__()

    def __post_init__(self) -> None:
        ...

    @property
    def entity_meta(self) -> "EntityMeta":
        return self.__entity_meta

    @property
    def fig_id(self) -> str:
        return self.__entity_meta["fig_id"]

    @property
    def tbl(self) -> Element:
        return self.__tbl

    @property
    def parent_fig_id(self) -> Optional[str]:
        return self.__entity_meta.get("parent_fig_id", None)

    @property
    def title(self) -> Optional[str]:
        return self.__entity_meta.get("title", None)

    def extract_data_subtbls(self, entity_base: "EntityMeta", data: Element) -> Iterator["Entity"]:
        tbls = Xpath.elems(data, "./table")
        assert len(tbls) <= 1, "invariant broken - expected each field to have at most 1 sub-table"
        if len(tbls) == 0:
            return
        # elif len(tbls) > 1:
        #     # TODO: remove iff invariant above holds
        #     for ndx, tbl in enumerate(tbls):
        #         ent = {**entity_base}
        #         ent["fig_id"] = f"""{ent["fig_id"]}{ndx}"""
        #         yield from self.__parse(ent, tbl)
        else:
            yield from self.__parse(entity_base, tbls[0])

    def __call__(self) -> Iterator["Entity"]:
        # must drive the process from this fn
        ...
