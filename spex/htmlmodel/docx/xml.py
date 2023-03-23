from typing import Optional, List, Iterable, Callable, Union
from lxml import etree
from lxml.etree import _Element, _ElementTree
from spex.htmlmodel.docx.types import NsMap
from typing import Mapping, cast


Element = _Element
ElementTree = _ElementTree
XmlElem = Union[_Element, _ElementTree]


def fmt(elem: _Element) -> str:
    """render XML element into a formatted string."""
    return etree.tostring(elem, pretty_print=True, encoding="unicode")


def pp(elem: _Element) -> None:
    """pretty-print XML element."""
    print(fmt(elem))


def spit(path: str, elem: _Element) -> None:
    """spit XML element out into a file."""
    with open(path, "w") as fh:
        fh.write(fmt(elem))


def next_while(e: _Element, pred: Callable[[_Element], bool]) -> Iterable[_Element]:
    while True:
        e_nxt = e.getnext()
        if e_nxt and pred(e_nxt):
            yield e_nxt
        else:
            break


class Xpath:
    @staticmethod
    def __nsmap_or_elem_nsmap(e: _Element, nsmap: Optional[NsMap]) -> NsMap:
        return nsmap if nsmap is not None else cast(Mapping[str, str], e.nsmap)

    @classmethod
    def elems(
        cls, e: _Element, query: str, nsmap: Optional[NsMap] = None
    ) -> List[_Element]:
        res = e.xpath(query, namespaces=cls.__nsmap_or_elem_nsmap(e, nsmap))
        assert isinstance(res, list)
        if len(res) > 0 and not isinstance(res[0], _Element):
            if query.startswith("@") or "/@" in query:
                raise RuntimeError(
                    "don't query attribute values with this function, use `Xpath.attrs`"
                )
            else:
                raise RuntimeError(
                    f"query '{query}' did not return a list of _Element, first element is {type(res[0])}"
                )
        return cast(List[_Element], res)

    @classmethod
    def elem_first(
        cls, e: _Element, query: str, nsmap: Optional[NsMap] = None
    ) -> Optional[_Element]:
        res = cls.elems(e, query, nsmap)
        return res[0] if len(res) > 0 else None

    @classmethod
    def elem_first_req(
        cls, e: _Element, query: str, nsmap: Optional[NsMap] = None
    ) -> _Element:
        res = cls.elems(e, query, nsmap)
        if len(res) == 0:
            raise RuntimeError("failed to find required element")
        return res[0]

    @classmethod
    def attrs(cls, e: _Element, query: str, nsmap: Optional[NsMap] = None) -> List[str]:
        res = e.xpath(query, namespaces=cls.__nsmap_or_elem_nsmap(e, nsmap))
        assert isinstance(res, list)
        if len(res) > 0 and not isinstance(res[0], str):
            raise RuntimeError(
                f"query should return a list of str elements for attr-queries, got {type(res[0])}, use `Xpath.elems` instead?"
            )
        return cast(List[str], res)

    @classmethod
    def attr_first(
        cls, e: _Element, query: str, nsmap: Optional[NsMap] = None
    ) -> Optional[str]:
        res = cls.attrs(e, query, nsmap)
        return res[0] if len(res) > 0 else None

    @classmethod
    def attr_first_req(
        cls, e: _Element, query: str, nsmap: Optional[NsMap] = None
    ) -> str:
        res = cls.attrs(e, query, nsmap)
        if len(res) == 0:
            raise RuntimeError("failed to find required attribute")
        return res[0]
