from pathlib import Path
from typing import List, Optional

from lxml.etree import _Element

from spex.htmlspec.docx.docxutils import docx_extract_contents
from spex.htmlspec.docx.header import Header
from spex.htmlspec.docx.numbering import NumberingDocument
from spex.htmlspec.docx.runproperties import RunProperties
from spex.htmlspec.docx.styles import StylesDocument
from spex.htmlspec.docx.tags import Tag
from spex.xml import Xpath


class Document:
    __numbering_xml: Optional[NumberingDocument]
    __header: Header

    def __init__(self, doc_path: Path):
        assert doc_path.exists(), "provided document does not exist"
        self._elem = docx_extract_contents(doc_path, "word/document.xml")
        self.__path = doc_path
        try:
            self.__numbering_xml = NumberingDocument(doc_path)
        except KeyError:
            # not all documents have a numbering.xml file
            # (presumably only if it contains lists)
            self.__numbering_xml = None
        self.__header = Header(doc_path)
        self.__styles = StylesDocument(doc_path)

    def __repr__(self) -> str:
        return f"{type(self).__name__}<path: {str(self.__path)}>"

    @property
    def header(self) -> Header:
        return self.__header

    @property
    def path(self) -> Path:
        """path to document."""
        return self.__path

    @property
    def tables(self) -> List[_Element]:
        return Xpath.elems(self._elem, ".//w:tbl")

    @property
    def numbering_xml(self) -> Optional[NumberingDocument]:
        return self.__numbering_xml

    @property
    def styles(self) -> StylesDocument:
        return self.__styles

    def extract_p_rpr(self, elem: _Element) -> Optional[RunProperties]:
        """extract run properties from paragraph's pStyle and rPr.

        NOTE: according to http://officeopenxml.com/WPparagraphProperties.php
              this styling only applies to the paragraph glyph itself.
              In other words, don't use the properties derived from this for
              styling the text runs themselves."""
        assert elem.tag == Tag.p.value, f"expected paragraph (w:p) tag, got: {elem.tag}"
        style_id = Xpath.attr_first(elem, "./w:pPr/w:pStyle/@w:val")
        pstyle = self.styles.get_pstyle(style_id) if style_id is not None else None
        p_rpr_elem = Xpath.elem_first(elem, "./w:pPr/w:rPr")
        rpr = RunProperties.from_rpr_elem(p_rpr_elem)
        if pstyle is None:
            return rpr
        return pstyle.merge(rpr) if rpr is not None else pstyle

    def extract_r_rpr(self, elem: _Element) -> Optional[RunProperties]:
        assert elem.tag == Tag.r.value, f"expected run (w:r) tag, got: {elem.tag}"
        r_rpr_elem = Xpath.elem_first(elem, "./w:rPr")
        if r_rpr_elem is None:
            return None
        r_rpr = RunProperties.from_rpr_elem(r_rpr_elem)
        rstyle_id = Xpath.attr_first(r_rpr_elem, "./w:rStyle/@w:val")
        rstyle = self.styles.get_cstyle(rstyle_id) if rstyle_id is not None else None
        if rstyle is None:
            return r_rpr
        return rstyle.merge(r_rpr)
