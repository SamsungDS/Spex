from typing import TYPE_CHECKING, Optional
from spexs2.xml import Xpath


if TYPE_CHECKING:
    from spexs2.xml import Element


def content_extract_brief(row: "Element", data: "Element", brief_maxlen=60) -> Optional[str]:
    p1_opt = Xpath.elem_first(data, "./p[1]")
    if p1_opt is None:
        return None
    p1 = p1_opt
    txt = "".join(
        # typestubs say we can receive either str's or byte's
        e.decode("utf-8") if isinstance(e, bytes) else e
        for e in p1.itertext()).strip()
    if ":" not in txt:
        return None
    brief = txt.split(":", 1)[1].strip().rstrip(".")
    if len(brief) <= brief_maxlen:
        return brief
    _brief = brief.split(".", 1)[0]
    return _brief if len(_brief) <= brief_maxlen else None
