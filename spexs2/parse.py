from typing import TYPE_CHECKING, Optional
from spexs2.xml import etree, Xpath
from spexs2.document import DocumentParser
from spexs2.quirks import QUIRKS_MAP

if TYPE_CHECKING:
    from spexs2.quirks import QuirksMap
    from pathlib import Path
    from spexs2.defs import Entity


# TODO determine what to return
def parse_document(spec: "Path", *, quirks_map: Optional["QuirksMap"] = None) -> "Entity":
    if quirks_map is None:
        quirks_map = QUIRKS_MAP

    doc = etree.parse(str(spec.absolute()))

    doc_spec = Xpath.attr_first(doc, "./head/meta/@data-spec")
    doc_rev = Xpath.attr_first(doc, "./head/meta/@data-revision")
    quirks_key = (doc_spec.lower().strip(), doc_rev.lower().strip())
    dp = quirks_map.get(quirks_key, DocumentParser)(doc, doc_spec, doc_rev)
    # TODO: determine exactly what we do here and what we return.
    yield from dp.parse()
