# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path
from typing import Dict, List

import lxml
import lxml.etree

from spex.xml import XmlUtils, Xpath, etree


def get_erroneous_figures(figures: List[str], html_doc: Path) -> Dict[str, str]:
    doc = etree.parse(html_doc)
    _err_figures: Dict[str, str] = {}
    for figure in figures:
        figure_id = figure.split("_")[0]
        try:
            p = Xpath.elem_first(doc, f"./body/table[@id={figure_id}]")
            if p is not None:
                _err_figures[figure] = XmlUtils.fmt(p)
        except lxml.etree.XPathEvalError:
            ...

    return _err_figures
