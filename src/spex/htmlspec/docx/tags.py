# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from enum import Enum

_nsmap = {
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "o": "urn:schemas-microsoft-com:office:office",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "v": "urn:schemas-microsoft-com:vml",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w10": "urn:schemas-microsoft-com:office:word",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "wne": "http://schemas.microsoft.com/office/word/2006/wordml",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "wpc": "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "wpi": "http://schemas.microsoft.com/office/word/2010/wordprocessingInk",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
}


def _expand(tag: str) -> str:
    """
    Expand tag such as `w:tbl` into the absolute
    format used by lxml etree.Element.tag.
    """
    ns, tagname = tag.split(":")
    return f"{{{_nsmap[ns]}}}{tagname}"


class Tag(Enum):
    tbl = _expand("w:tbl")  # table
    tr = _expand("w:tr")  # table row
    tc = _expand("w:tc")  # table cell
    p = _expand("w:p")  # paragraph
    pPr = _expand("w:pPr")  # paragraph properties
    r = _expand("w:r")  # run
    rPr = _expand("w:rPr")  # run properties
    b = _expand("w:b")  # bold
    i = _expand("w:i")  # italics
    u = _expand("w:u")  # underline
    strike = _expand("w:strike")  # strike(through)
    vertAlign = _expand("w:vertAlign")
    sz = _expand("w:sz")  # sz, size
    color = _expand("w:color")  # color
    t = _expand("w:t")  # text
    hyperlink = _expand("w:hyperlink")


__all__ = ["Tag"]
