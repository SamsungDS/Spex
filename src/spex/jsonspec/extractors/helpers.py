# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, Optional, Union

from spex.jsonspec.extractors.regular_expressions import (
    ELLIPSIS_LABEL_REGEX,
    LABEL_VALIDATION_REGEX,
    STRUCT_LABEL_REGEX,
)
from spex.jsonspec.lint import Linter, LintErr
from spex.xml import XmlUtils, Xpath

if TYPE_CHECKING:
    from spex.xml import Element


def extract_content(data: "Element") -> Optional[str]:
    maybe_paragraph = Xpath.elem_first(data, "./p[1]")
    if maybe_paragraph is None:
        return None
    paragraph = maybe_paragraph
    return XmlUtils.to_text(paragraph)


def content_extract_brief(content: str, brief_maxlen: int = 60) -> Optional[str]:
    """Extract brief from a string

    Args:
        content (str): Content string
        brief_maxlen (int, optional): Max length of the output string. Defaults to 60.

    Returns:
        Optional[str]: Brief
    """
    txt = content
    if txt is None or ":" not in txt:
        return None

    match = STRUCT_LABEL_REGEX.regex.match(txt)
    if match is None or match.group("brief") is None:
        return None
    brief = match.group("brief").rstrip(".").lstrip(" ")

    if len(brief) <= brief_maxlen:
        return brief
    _brief = brief.split(".", 1)[0]
    return _brief if len(_brief) <= brief_maxlen else None


def generate_acronym(text: str) -> str:
    """Generate a acronym from a text string

    It will use the first character of every word and concatenate it together
    to a string.

    Args:
        text (str): Text string

    Returns:
        str: String that contains the acronym
    """
    return "".join(w[0] for w in text.split()).lower()


def normalize_label(label: str) -> str:
    """Normalize a input string by replacing specific characters

    such as white space(" ") are replaced by underscore("_").

    Args:
        label (str): Input string

    Returns:
        str: Normalized string
    """
    return (
        label.lstrip()
        .rstrip()
        .replace(" ", "_")
        .replace("/", "")
        .replace("-", "_")
        .replace("__", "_")
        .upper()
    )


def validate_label(lbl: str, fig_id: str, row_key: str, linter: Linter) -> None:
    """Validate that a label conforms to a set of rules

    Args:
        lbl (str): The label as a string
        fig_id (str): figure id associated with the label
        row_key (str): row key associated with the label
        linter (Linter): linter used if validation fails
    """
    if (
        LABEL_VALIDATION_REGEX.match(lbl) is None
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
        the extractor failed to identify a column where this semantic component
        could be found.
    """
    if m is None:
        return True

    for field in fields(m):
        if getattr(m, field.name) is None:
            return True
    return False
