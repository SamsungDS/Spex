from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Union, Iterator, Type, Any, Callable, TypeVar
from spex.xml import Xpath
from spex.htmlmodel.docx.docxutils import docx_extract_contents


@dataclass(frozen=True)
class AbstractNumLvl:
    abstract_num_id: int
    ilvl: int
    num_fmt: str
    lvl_text: str

    def __post_init__(self):
        assert isinstance(self.abstract_num_id, int), "`num_id` should be an integer"
        assert isinstance(self.ilvl, int), "`ilvl` should be an integer"

    __ol_styles: Dict[str, str] = field(default_factory=lambda:{
        # TODO: plot in further values.
        "decimal": "decimal",
        "lowerLetter": "lower-alpha",
        "lowerRoman": "lower-roman",
    })

    @property
    def is_ordered(self) -> bool:
        return self.lvl_text.startswith("%")

    @property
    def tag(self) -> str:
        return "ol" if self.is_ordered else "ul"

    @property
    def css_clsname(self) -> str:
        return f"{self.tag}{self.abstract_num_id}"

    def to_css(self) -> str:
        is_ordered = self.is_ordered
        ilvl = self.ilvl
        tag = self.tag
        clsname = self.css_clsname
        tags = " ".join(tag for _ in range(ilvl))
        # TODO: determine CSS list style.
        if is_ordered:
            style = self.__ol_styles.get(self.num_fmt, "decimal")
        else:
            # word defaults to alternating between two styles for unordered lists.
            ul_styles = ["disc", "circle"]
            style = ul_styles[ilvl % len(ul_styles)]
        if tags:
            return f"{tag}.{clsname} {tags} {{ list-style-type: {style}; }}"
        else:
            return f"{tag}.{clsname} {{ list-style-type: {style}; }}"


T = TypeVar("T")


def coerce(v: Any, t: Type[T], f: Callable[[Any], T]) -> T:
    if v is None:
        raise Exception("expected a value")
    cv = f(v)
    if not isinstance(cv, t):
        raise Exception(f"expected value of type {t}, got {type(cv)}")
    return cv


@dataclass(frozen=True)
class AbstractNum:
    abstract_num_id: int
    ilvls: List[AbstractNumLvl]

    def get_ilvl(self, ilvl: Union[str, int]) -> AbstractNumLvl:
        return self.ilvls[int(ilvl)]


class NumberingDocument:
    _abstract_nums: Dict[int, AbstractNum]
    _num_to_abs_num: Dict[int, int]

    def __init__(self, doc_path: Path):
        self._elem = docx_extract_contents(doc_path, "word/numbering.xml")
        self._path = doc_path
        self.__parse_absnum()

    def has_num_id(self, num_id: Union[str, int]) -> bool:
        """true if num_id points to a defined numbering style."""
        return int(num_id) in self._num_to_abs_num

    def get_style(self, num_id: Union[str, int]) -> AbstractNum:
        if int(num_id) == 0:
            breakpoint()
        return self._abstract_nums[self._num_to_abs_num[int(num_id)]]
        # return self.__abstract_nums[int(num_id)]

    def iter_styles(self) -> Iterator[AbstractNum]:
        yield from self._abstract_nums.values()

    def __parse_absnum(self) -> None:
        abs_nums = {}
        abs_num_elems = Xpath.elems(self._elem, "./w:abstractNum")
        for abs_num in abs_num_elems:
            ilvls = []
            num_id = int(Xpath.attr_first_req(abs_num, "./@w:abstractNumId"))
            for ilvl in Xpath.elems(abs_num, "./w:lvl"):
                s_ilvl = int(Xpath.attr_first_req(ilvl, "./@w:ilvl"))
                s_fmt = Xpath.attr_first_req(ilvl, "./w:numFmt/@w:val")
                s_txt = Xpath.attr_first_req(ilvl, "./w:lvlText/@w:val")
                ilvls.append(
                    AbstractNumLvl(
                        abstract_num_id=num_id,
                        ilvl=s_ilvl,
                        num_fmt=s_fmt,
                        lvl_text=s_txt,
                    )
                )
            abs_nums[num_id] = AbstractNum(abstract_num_id=num_id, ilvls=ilvls)
        self._abstract_nums = abs_nums

        num_elems = Xpath.elems(self._elem, "./w:num")
        num_to_abs_num: Dict[int, int] = {}
        for num_elem in num_elems:
            num_id = coerce(Xpath.attr_first(num_elem, "@w:numId"), int, int)
            abs_num_id = coerce(
                Xpath.attr_first(num_elem, "./w:abstractNumId/@w:val"), int, int
            )
            num_to_abs_num[num_id] = abs_num_id
        self._num_to_abs_num = num_to_abs_num

    def __repr__(self) -> str:
        return f"{type(self).__name__}<path: {str(self._path)}>"

    @property
    def path(self) -> Path:
        """path to document."""
        return self._path
