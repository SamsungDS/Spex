# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause


from dataclasses import dataclass
from re import DOTALL, Pattern, compile
from typing import Optional, Tuple


@dataclass(frozen=True)
class ContentRegex:
    regex: Pattern

    def match(self, text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """_summary_

        Args:
            text (str): Text string to try to match the regex on

        Returns:
            Tuple[Optional[str], Optional[str], Optional[str]]: Returns tuple with
            the following fields:

            * label
            * acronym
            * brief
        """
        _match = STRUCT_LABEL_REGEX.regex.match(text)
        label: Optional[str] = None
        acronym: Optional[str] = None
        brief: Optional[str] = None

        if _match is None:
            return None, None, None
        elif _match.group("acronym") is not None and _match.group("acronym") != "":
            acronym = _match.group("acronym")
        elif _match.group("label") is not None and _match.group("label") != "":
            label = _match.group("label")
        elif _match.group("brief") is not None and _match.group("brief") != "":
            brief = _match.group("brief")
        return label, acronym, brief


STRUCT_LABEL_REGEX = ContentRegex(
    compile(
        r"^(?P<label>[\w\s,-/&]*)\(?(?P<acronym>[\w\s\d]*)?\)?:?(?P<brief>.+)?$",  # noqa
        DOTALL,
    )
)

VALUE_LABEL_REGEX = ContentRegex(
    compile(
        r"^(?P<label>[\w\s/-]*):?(?P<brief>.+)?$",  # noqa
        DOTALL,
    )
)

RANGE_REGEX = compile(r"(?P<high>\d+)\s*(:\s*(?P<low>\d+))?")

DYNAMIC_RANGE_REGEX = compile(
    r"^(?P<low>[a-zA-Z0-9+\-*()\s]+):(?P<high>[a-zA-Z0-9+\-*()\s]+)"
)

ELLIPSIS_LABEL_REGEX = compile(r"^[\s]*[\.\.\.]|[…][\s]*$")

LABEL_VALIDATION_REGEX = compile(r"^[a-zA-Z][\w]*$")

LABEL_NUMERICAL_REARRANGE_REGEX = compile(r"^(\d+)(.*)")

TABLE_ID_REGEX = compile(r"^Figure (?P<id>\d+):.*")
