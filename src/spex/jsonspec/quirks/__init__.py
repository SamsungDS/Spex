# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from typing import TYPE_CHECKING, Dict, Tuple, Type

from spex.jsonspec.quirks.kv import NvmKv1_0c
from spex.jsonspec.quirks.mi import NvmMi1_2c
from spex.jsonspec.quirks.nvm import NvmCmdSet1c
from spex.jsonspec.quirks.zoned import NvmCsZoned11c

if TYPE_CHECKING:
    from spex.jsonspec.document import DocumentParser


QuirksMap = Dict[Tuple[str, str], Type["DocumentParser"]]

QUIRKS_MAP: QuirksMap = {
    ("nvm express® nvm command set specification", "1.0c"): NvmCmdSet1c,
    ("nvm express® zoned namespace command set specification", "1.1c"): NvmCsZoned11c,
    ("nvm express® management interface specification", "1.2c"): NvmMi1_2c,
    ("nvm express® key value command set specification", "1.0c"): NvmKv1_0c,
    ("nvm express® key value command set specification", "1.0"): NvmKv1_0c,
}
