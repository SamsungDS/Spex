from pathlib import Path
from typing import IO
import zipfile
from lxml import etree


def docx_extract_contents(docx_path: Path, file: str = "word/document.xml") -> etree._Element:
    with zipfile.ZipFile(docx_path, "r") as zfile:
        fh: IO[bytes]
        with zfile.open(file) as fh:
            return etree.fromstring(fh.read())
