from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Iterator, Tuple
from spexs2.xml import Element, Xpath
from spexs2.lint import Linter, LintEntry, Code
from spexs2 import xml  # TODO: for debugging


if TYPE_CHECKING:
    from spexs2.defs import EntityMeta, ParseFn, Entity
    from spexs2.document import DocumentParser


RowResult = Tuple[Element, Element, Element]


class FigureExtractor(ABC):
    BRIEF_MAXLEN: int = 60
    __linter: Linter

    def __init__(self,
                 doc_parser: "DocumentParser",
                 entity_meta: "EntityMeta",
                 tbl: Element,
                 parse_fn: "ParseFn",
                 linter: Linter):
        self.doc_parser = doc_parser
        self.__entity_meta = entity_meta
        self.__tbl = tbl
        self.__parse = parse_fn
        self.__linter = linter
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

    @property
    def linter(self) -> Linter:
        return self.__linter

    def add_issue(self, code: Code, *,
                  fig: Optional[str] = None,
                  msg: str = "",
                  row_key: Optional[str] = None) -> LintEntry:
        return self.__linter.add_issue(code,
                                       fig if fig is not None else self.fig_id,
                                       msg=msg, row=row_key)

    def row_iter(self) -> Iterator[Element]:
        # select first td where parent is a tr
        # ... then select the parent (tr) again
        # -> filters out header (th) rows
        yield from Xpath.elems(self.tbl, "./tr/td[1]/parent::tr")

    def rows_on_err(self, row, err: Exception) -> Optional[RowResult]:
        row_txt = "".join(row.itertext()).lstrip().lower()
        if row_txt.startswith("…"):
            return None  # SKIP
        elif row_txt.startswith("notes:"):
            raise StopIteration  # abort further processing
        else:
            raise err  # propagate actual error

    def rows(self) -> Iterator[RowResult]:
        for row in self.row_iter():
            try:
                yield row, self.val_extract(row), self.data_extract(row)
            except StopIteration:
                return
            except Exception as e:
                try:
                    return self.rows_on_err(row, e)
                except StopIteration:
                    return
                except Exception as err:
                    if err != e:
                        raise err from e
                    else:
                        raise e

    def extract_data_subtbls(self, entity_base: "EntityMeta", data: Element) -> Iterator["Entity"]:
        tbls = Xpath.elems(data, "./table")
        assert len(tbls) <= 1, "invariant broken - expected each field to have at most 1 sub-table"
        if len(tbls) == 0:
            return
        else:
            yield from self.__parse(entity_base, tbls[0])

    @abstractmethod
    def __call__(self) -> Iterator["Entity"]:
        # must drive the process from this fn
        ...

    @abstractmethod
    def val_extract(self, row: Element) -> Element:
        ...

    @abstractmethod
    def data_extract(self, row: Element) -> Element:
        ...
