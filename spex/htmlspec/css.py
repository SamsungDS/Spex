from typing import Dict, List, Optional, Protocol, Union

from gcgen.api import Section


def css_block(
    s: Section, selectors: Union[List[str], str], attrs: Dict[str, str]
) -> None:
    if isinstance(selectors, list):
        selectors = ", ".join(selectors)
    s.emitln(f"{selectors} {{").indent()
    for attr, val in attrs.items():
        s.emitln(f"{attr}: {val};")
    s.dedent().emitln("}")


class CssObj(Protocol):
    @property
    def css_attrs(self) -> Dict[str, str]:
        ...


class CssCache:
    def __init__(self, prefix: str):
        self.__cache: Dict[CssObj, str] = {}
        self.__prefix = prefix
        self.__counter = 0

    def get_clsname(self, elem: CssObj) -> Optional[str]:
        if elem is None or elem.css_attrs == {}:
            return None

        clsname = self.__cache.get(elem, None)
        if clsname is not None:
            return clsname

        count = self.__counter
        self.__counter += 1
        clsname = f"{self.__prefix}{count}"
        self.__cache[elem] = clsname
        return clsname

    def emit_rules(self, s: Section):
        for css_obj, clsname in self.__cache.items():
            css_block(s, f".{clsname}", css_obj.css_attrs)
