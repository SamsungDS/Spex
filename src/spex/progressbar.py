# SPDX-FileCopyrightText: 2024 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from typing import Tuple, TypeAlias

ParseProgressStatus: TypeAlias = Tuple[
    str, int, int
]  # (<phase>, <figure>, <of figures>)
