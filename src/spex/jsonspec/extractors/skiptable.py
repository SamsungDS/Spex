# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from typing import Iterator, List

from spex.jsonspec.defs import Entity
from spex.jsonspec.extractors.figure import FigureExtractor


class SkipTable(FigureExtractor):
    @classmethod
    def can_apply(cls, tbl_col_hdrs: List[str]) -> bool:
        raise RuntimeError(
            "Don't add Skiptable to `extractors`, implied if no extractor can be applied."
        )

    def __call__(self) -> Iterator[Entity]:
        yield from ()
        return
