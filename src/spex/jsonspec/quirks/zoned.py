# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from spex.jsonspec.document import DocumentParser


class NvmCsZoned11c(DocumentParser):
    label_overrides = {
        ("37", "0"): "zt",
        ("37", "1"): "zs",
        ("37", "2"): "za",
    }

    fig_extractor_overrides = {}
