# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

from lxml.etree import _Element

from spex.htmlspec.docx.docxutils import docx_extract_contents
from spex.htmlspec.docx.runproperties import RunProperties
from spex.xml import Xpath


class StyleResolver:
    # translate from potential alias to the canonical style id (name)
    _style_aliases: Dict[str, str]

    def __init__(self, style_doc: _Element, style_type: str):
        self._style_doc = style_doc
        assert style_type in ("paragraph", "character")
        self._style_type = style_type
        self._style_aliases = self.__init_alias_dct(style_doc, style_type)

    @staticmethod
    def __init_alias_dct(style_doc: _Element, style_type: str) -> Dict[str, str]:
        alias_dct: Dict[str, str] = {}
        for style in Xpath.elems(style_doc, f"./w:style[@w:type = '{style_type}']"):
            canonical_style_name = Xpath.attr_first_req(style, "@w:styleId")
            alias_dct[canonical_style_name] = canonical_style_name

            aliases = Xpath.attr_first(style, "./w:aliases/@w:val") or ""
            for alias in (a.strip() for a in aliases.split(",")):
                alias_dct[alias] = canonical_style_name

        return alias_dct

    @lru_cache(maxsize=60)
    def __get_style(self, style_id: str) -> Optional[RunProperties]:
        # get entry
        # if w:basedOn exists, resolv (using same fn, causing caching), return merge(<basedOn>, <this>)
        style = Xpath.elem_first_req(
            self._style_doc,
            f"./w:style[@w:type = '{self._style_type}'][@w:styleId = '{style_id}']",
        )
        based_on = Xpath.attr_first(style, "./w:basedOn/@w:val")
        rpr = RunProperties.from_rpr_elem(Xpath.elem_first(style, "./w:rPr"))
        if based_on is None:
            # style is stand-alone
            return rpr
        # style extends some other base style
        based_on_rpr = self.__get_style(based_on)
        return based_on_rpr.merge(rpr) if based_on_rpr is not None else rpr

    def get_style(self, style_id: str) -> Optional[RunProperties]:
        canonical_style_name = self._style_aliases[style_id]
        return self.__get_style(canonical_style_name)


class StylesDocument:
    def __init__(self, doc_path: Path):
        self._elem = docx_extract_contents(doc_path, "word/styles.xml")
        self._path = doc_path
        self._pstyles = StyleResolver(self._elem, "paragraph")
        self._cstyles = StyleResolver(self._elem, "character")

    def get_pstyle(self, style_id: str) -> Optional[RunProperties]:
        return self._pstyles.get_style(style_id)

    def get_cstyle(self, style_id: str) -> Optional[RunProperties]:
        return self._cstyles.get_style(style_id)
