from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from spex.jsonspec.document import DocumentParser
from spex.jsonspec.quirks import QUIRKS_MAP, QuirksMap
from spex.xml import ElementTree, Xpath, etree


@dataclass(frozen=True)
class SpecDocument:
    tree: ElementTree
    key: str
    rev: str

    def get_parser(
        self, args: Namespace, quirks_map: Optional[QuirksMap] = None
    ) -> DocumentParser:
        if quirks_map is None:
            quirks_map = QUIRKS_MAP

        quirks_key = (self.key, self.rev)
        dp = quirks_map.get(quirks_key, DocumentParser)(
            args, self.tree, self.key, self.rev
        )
        return dp


# TODO determine what to return
def open_doc(spec: Path) -> SpecDocument:
    doc = etree.parse(str(spec.absolute()))

    doc_spec = Xpath.attr_first_req(doc, "./head/meta/@data-spec").lower()
    doc_rev = Xpath.attr_first_req(doc, "./head/meta/@data-revision").lower()
    return SpecDocument(tree=doc, key=doc_spec, rev=doc_rev)
