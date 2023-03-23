from pathlib import Path
from re import compile as re_compile
from typing import Optional
from spex.xml import Xpath
from spex.htmlmodel.docx.docxutils import docx_extract_contents

_rgx_revision = re_compile(r".*[Rr]evision\s+(?P<rev>\S+).*")


class Header:
    def __init__(self, doc_path: Path):
        self._elem = docx_extract_contents(doc_path, "word/header1.xml")
        self._path = doc_path
        self._header = "".join(
            e.text for e in Xpath.elems(self._elem, ".//w:t") if e.text is not None
        )
        m = _rgx_revision.match(self._header)
        self._revision = m.group("rev") if m is not None else None
        self._title = self._header.split(",")[0].strip()

    @property
    def header(self) -> str:
        return self._header

    @property
    def revision(self) -> Optional[str]:
        return self._revision

    @property
    def title(self) -> str:
        return self._title


__all__ = ["Header"]
