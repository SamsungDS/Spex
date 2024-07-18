# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass, fields
from re import compile as re_compile
from typing import TYPE_CHECKING, Optional, Union

from spex.jsonspec.extractors.regular_expressions import (
    ELLIPSIS_LABEL_REGEX,
    STRUCT_LABEL_REGEX,
)
from spex.jsonspec.lint import Linter, LintErr
from spex.xml import Xpath

if TYPE_CHECKING:
    from spex.xml import Element


def extract_content(data: "Element") -> Optional[str]:
    p1_opt = Xpath.elem_first(data, "./p[1]")
    if p1_opt is None:
        return None
    p1 = p1_opt
    txt: str = "".join(
        # typestubs say we can receive either str's or byte's
        e.decode("utf-8") if isinstance(e, bytes) else e
        for e in p1.itertext()
    ).strip()
    return txt


def content_extract_brief(
    row: "Element", data: "Element", brief_maxlen: int = 60
) -> Optional[str]:
    txt = extract_content(data=data)
    if txt is None or ":" not in txt:
        return None

    match = STRUCT_LABEL_REGEX.match(txt)
    if match is None or match.group("brief") is None:
        return None
    brief = match.group("brief").rstrip(".").lstrip(" ")

    if len(brief) <= brief_maxlen:
        return brief
    _brief = brief.split(".", 1)[0]
    return _brief if len(_brief) <= brief_maxlen else None


def generate_acronym(text: str) -> str:
    return "".join(w[0] for w in text.split()).lower()


def validate_label(lbl: str, fig_id: str, row_key: str, linter: Linter) -> None:
    if (
        STRUCT_LABEL_REGEX.match(lbl) is None
        and ELLIPSIS_LABEL_REGEX.match(lbl) is None
    ):
        linter.add_issue(
            LintErr.LBL_INVALID_CHRS, fig_id, row_key=row_key, ctx={"label": lbl}
        )


@dataclass(frozen=True)
class StructTableMapping:
    range_column: Optional[str]
    label_column: Optional[str]
    content_column: Optional[str]


@dataclass(frozen=True)
class ValueTableMapping:
    value_column: Optional[str]
    label_column: Optional[str]
    content_column: Optional[str]


Mapping = Union[StructTableMapping, ValueTableMapping]


def mapping_incomplete(m: Optional[Mapping]) -> bool:
    """return true iff any entry in the mapping is set to None (unbound).

    Args:
        m: a mapping instance

    Returns:
        True iff. any entry in the mapping table is None, signifying it is unbound, that
        the extractor failed to identify a column where this semantic component could be found.
    """
    if m is None:
        return True

    for field in fields(m):
        if getattr(m, field.name) is None:
            return True
    return False
