# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from typing import TYPE_CHECKING, Iterator, List, Optional

from spex.jsonspec.defs import Entity
from spex.jsonspec.extractors.figure import FigureExtractor

if TYPE_CHECKING:
    from spex.jsonspec.extractors.helpers import Mapping


class SkipTable(FigureExtractor):
    @classmethod
    def can_apply(cls, tbl_col_hdrs: List[str]) -> Optional["Mapping"]:
        raise RuntimeError(
            "Don't add Skiptable to `extractors`, implied if no extractor can be"
            "applied."
        )

    def __call__(self) -> Iterator[Entity]:
        yield from ()
        return
