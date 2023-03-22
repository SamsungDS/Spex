from typing import TYPE_CHECKING, Optional
from re import compile as re_compile
from spex.model.xml import Xpath
from spex.model.lint import Linter, LintErr


if TYPE_CHECKING:
    from spex.model.xml import Element

rgx_lbl = re_compile(r"""^[a-zA-Z_][\w]*$""")


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


def validate_label(lbl: str, fig_id: str, row_key: str, linter: Linter) -> None:
    if rgx_lbl.match(lbl) is None:
        linter.add_issue(
            LintErr.LBL_INVALID_CHRS, fig_id, row_key=row_key,
            ctx={"label": lbl}
        )
