from typing import List, Optional

from spex.xml import Element, XmlUtils, Xpath


def find_colspan(element: Element) -> List[Element]:
    q = Xpath.attrs_option(element, "./*[@colspan]/*")
    return q


def contains_th(element: Element) -> bool:
    q = Xpath.elem_first(element, "./th")
    return q is not None


def extract_possible_colspan(row: Element) -> Optional[str]:
    colspan = find_colspan(row)
    if colspan:
        text = "".join([XmlUtils.to_text(x) for x in colspan])
        return text
    return None
