# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

import copy
from enum import Enum
from typing import Dict, Optional, Union

from lxml.etree import _Element

from spex.xml import Xpath


class VertAlign(Enum):
    """vertical alignment of text."""

    baseline = 1
    subscript = 2
    superscript = 3


class RunProperties:
    """basic text-formatting properties.

    NOTE: in same cases (e.g. underline, color) only basic options are retained.
    This is by design. We want to produce HTML which is visually remniscient of
    the spec, while being easier to parse than the underlying docx XML.

    See http://officeopenxml.com/WPtextFormatting.php for details on how OOXML
    represents text-formatting options."""

    __vert_align: Union[None, VertAlign]

    def __init__(
        self,
        *,
        bold: Optional[bool],
        italics: Optional[bool],
        underline: Optional[bool],
        strikethrough: Optional[bool],
        vert_align: Union[None, VertAlign, str],
        size: Union[None, str, int],
        color: Optional[str],
    ):
        # w:b, w:bCs
        self.__bold = bold
        # w:i, w:iCs
        self.__italics = italics
        # w:u
        self.__underline = underline
        # w:strike
        self.__strikethrough = strikethrough
        # w:vertAlign
        if vert_align:
            self.__vert_align = (
                vert_align
                if isinstance(vert_align, VertAlign)
                else VertAlign[vert_align]
            )
        else:
            self.__vert_align = None
        # w:sz
        self.__size = int(size) if size else None
        # w:color
        if color is not None and len(color) != 6:
            # disregard 'auto' and similar non-hex values.
            color = None
        self.__color = color
        self.__css_attrs = self.__compute_css_attrs()

    @property
    def bold(self) -> bool:
        if self.__bold is None:
            return False
        return self.__bold

    @property
    def italics(self) -> bool:
        if self.__italics is None:
            return False
        return self.__italics

    @property
    def underline(self) -> bool:
        if self.__underline is None:
            return False
        return self.__underline

    @property
    def strikethrough(self) -> bool:
        if self.__strikethrough is None:
            return False
        return self.__strikethrough

    @property
    def vert_align(self) -> VertAlign:
        if self.__vert_align is None:
            return VertAlign.baseline
        return self.__vert_align

    @property
    def size(self) -> Optional[int]:
        if self.__size is None:
            return None
        return self.__size

    @property
    def color(self) -> Optional[str]:
        if self.__color is None:
            return None
        return self.__color

    @property
    def css_attrs(self) -> Dict[str, str]:
        return self.__css_attrs

    def __eq__(self, other):
        return type(other) == type(self) and self.__css_attrs == other.__css_attrs

    def __hash__(self):
        return hash(frozenset(self.__css_attrs))

    def __repr__(self):
        return repr(self.__css_attrs)

    def __copy__(self) -> "RunProperties":
        return type(self)(
            bold=self.__bold,
            italics=self.__italics,
            underline=self.__underline,
            strikethrough=self.__strikethrough,
            vert_align=self.__vert_align,
            size=self.__size,
            color=self.__color,
        )

    def merge(self, other: Optional["RunProperties"]) -> "RunProperties":
        """Produce new `RunProperties` instance from self and `other`.

        NOTE: keys from `other` override keys from self."""
        if other is None:
            return self
        c = copy.copy(self)

        if other.__bold is not None:
            c.__bold = other.__bold
        if other.__italics is not None:
            c.__italics = other.__italics
        if other.__underline is not None:
            c.__underline = other.__underline
        if other.__strikethrough is not None:
            c.__strikethrough = other.__strikethrough
        if other.__vert_align is not None:
            c.__vert_align = other.__vert_align
        if other.__size is not None:
            c.__size = other.__size
        if other.__color is not None:
            c.__color = other.__color

        # CSS attrs are normally computed after object initialization.
        # trigger re-computation due to (potentially) updated entries
        c.__css_attrs = c.__compute_css_attrs()

        return c

    def __compute_css_attrs(self) -> Dict[str, str]:
        attrs = {}
        if self.__bold is not None:
            attrs["font-weight"] = "bold" if self.__bold else "normal"
        if self.__italics is not None:
            attrs["font-style"] = "italic" if self.__italics else "normal"

        # underline and strikethrough (line-through) are governed by the same
        # css property.
        txt_dec_line = []
        if self.__underline is not None:
            txt_dec_line.append("underline")
        if self.__strikethrough is not None:
            txt_dec_line.append("line-through")
        if txt_dec_line:
            attrs["text-decoration-line"] = " ".join(txt_dec_line)
        # TODO: what to do to support vertAlign?
        #  Super- & Subscript are not directly supported and require fiddling
        #  with additional CSS properties.
        if self.__vert_align is not None:
            va = self.__vert_align
            if va == VertAlign.baseline:
                attrs["vertical-align"] = "baseline"
            elif va == VertAlign.subscript:
                attrs["vertical-align"] = "sub"
            elif va == VertAlign.superscript:
                attrs["vertical-align"] = "super"
        if self.__size is not None:
            # TODO: should we do more than converting to points?
            sz = int(self.__size) / 2.0
            attrs["font-size"] = f"{sz}pt"
        if self.__color is not None:
            attrs["color"] = f"#{self.__color}"
        return attrs

    @classmethod
    def from_rpr_elem(cls, rpr_xml: Optional[_Element]) -> Optional["RunProperties"]:
        if rpr_xml is None:
            return None

        def bprop_val(e: _Element, selector: str, attr: str) -> Optional[bool]:
            # b, i and strike elems all follow same approach:
            # if element is absent -> None
            #   ...because we use this value to signal that the rPr did
            #   not explicitly disable the prop either.
            # if present w/o w:val attr -> True
            # if present with w:val attr -> "1" is True, "0" is false
            r1 = Xpath.elem_first(e, selector)
            if r1 is None:
                return None
            r2 = Xpath.attr_first(r1, "./@w:val")
            return r2 is None or r2.strip() != "0"

        def u_val(e: _Element) -> Optional[bool]:
            r1 = Xpath.elem_first(e, "./w:u")
            if r1 is None:
                return None
            r2 = Xpath.attr_first_req(r1, "./@w:val")
            return r2 != "none"

        rpr = RunProperties(
            bold=bprop_val(rpr_xml, "./w:b", "w:val"),
            italics=bprop_val(rpr_xml, "./w:i", "w:val"),
            underline=u_val(rpr_xml),
            strikethrough=bprop_val(rpr_xml, "./w:strike", "w:val"),
            vert_align=Xpath.attr_first(rpr_xml, "./w:vertAlign/@w:val"),
            # explicitly disable support for font sizes - this gives a nicer output.
            # size=xml.xpath_first(rpr_xml, "./w:sz/@w:val"),
            size=None,
            color=Xpath.attr_first(rpr_xml, "./w:color/@w:val"),
        )
        return rpr
