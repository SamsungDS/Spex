# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from typing import List, Mapping, Optional, Union, cast

from lxml import etree
from lxml.etree import _Element, _ElementTree

Element = _Element
ElementTree = _ElementTree
XmlElem = Union[_Element, _ElementTree]


class XmlUtils:
    @staticmethod
    def fmt(elem: XmlElem) -> str:
        """render XML element into a formatted string."""
        return etree.tostring(elem, pretty_print=True, encoding="unicode")

    @staticmethod
    def pp(elem: XmlElem) -> None:
        """pretty-print XML element."""
        print(XmlUtils.fmt(elem))

    @staticmethod
    def spit(path: str, elem: XmlElem) -> None:
        """spit XML element out into a file."""
        with open(path, "w") as fh:
            fh.write(XmlUtils.fmt(elem))

    @staticmethod
    def to_text(elem: XmlElem) -> str:
        if isinstance(elem, _ElementTree):
            elem = elem.getroot()
        return "".join(
            e.decode("utf-8") if isinstance(e, bytes) else e for e in elem.itertext()
        ).strip()


class Xpath:
    @classmethod
    def elems(cls, e: XmlElem, query: str) -> List[Element]:
        if isinstance(e, _ElementTree):
            e = e.getroot()
        res = e.xpath(query, namespaces=cast(Mapping[str, str], e.nsmap))
        assert isinstance(res, list)
        # cannot use type Element with isinstance
        if len(res) > 0 and not isinstance(res[0], (_Element, _ElementTree)):
            if query.startswith("@") or "/@" in query:
                raise RuntimeError(
                    "don't query attribute values with this function, use `Xpath.attrs`"
                )
            else:
                raise RuntimeError(
                    f"query '{query}' did not return a list of Element, "
                    f"first element is {type(res[0])}"
                )
        return cast(List[Element], res)

    @classmethod
    def elem_first(cls, e: XmlElem, query: str) -> Optional[Element]:
        res = cls.elems(e, query)
        return res[0] if len(res) > 0 else None

    @classmethod
    def elem_first_req(cls, e: Union[ElementTree, Element], query: str) -> Element:
        res = cls.elems(e, query)
        if len(res) == 0:
            raise RuntimeError("failed to find required element")
        return res[0]

    @classmethod
    def attrs(cls, e: XmlElem, query: str) -> List[str]:
        if isinstance(e, _ElementTree):
            e = e.getroot()
        res = e.xpath(query, namespaces=cast(Mapping[str, str], e.nsmap))
        assert isinstance(res, list)
        if len(res) > 0 and not isinstance(res[0], str):
            raise RuntimeError(
                "query should return a list of str elements for attr-queries, "
                f"got {type(res[0])}, use `Xpath.elems` instead?"
            )
        return cast(List[str], res)

    @classmethod
    def attr_first(cls, e: XmlElem, query: str) -> Optional[str]:
        res = cls.attrs(e, query)
        return res[0] if len(res) > 0 else None

    @classmethod
    def attr_first_req(
        cls,
        e: XmlElem,
        query: str,
    ) -> str:
        res = cls.attrs(e, query)
        if len(res) == 0:
            raise RuntimeError("failed to find required attribute")
        return res[0]


__all__ = ["etree", "Element", "ElementTree", "XmlElem", "Xpath", "XmlUtils"]
