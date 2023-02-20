from pathlib import Path
from re import compile as re_compile
from typing import Iterator, Tuple, Optional, TypedDict, Protocol, List, Dict, Type, NotRequired, Union
from gcgen.api import Scope, generator, write_file
from spexs2.xml import Element, etree, Xpath
from spexs2 import xml  # TODO: for debugging
from abc import abstractmethod, ABC


class EntityMeta(TypedDict):
    title: NotRequired[str]
    fig_id: str
    parent_fig_id: NotRequired[str]


class Entity(TypedDict):
    type: str
    title: NotRequired[str]
    fig_id: str
    parent_fig_id: NotRequired[str]
    data: dict


class ParseFn(Protocol):
    def __call__(self, entity: EntityMeta, tbl: Element) -> Iterator[Entity]: ...


class FigureExtractor:
    BRIEF_MAXLEN: int = 60

    def __init__(self,
                 doc_parser: "DocumentParser",
                 entity_meta: EntityMeta,
                 tbl: Element,
                 parse_fn: ParseFn):
        self.doc_parser = doc_parser
        self.__entity_meta = entity_meta
        self.__tbl = tbl
        self.__parse = parse_fn
        self.__post_init__()

    def __post_init__(self) -> None:
        ...

    @property
    def entity_meta(self) -> EntityMeta:
        return self.__entity_meta

    @property
    def fig_id(self) -> str:
        return self.__entity_meta["fig_id"]

    @property
    def tbl(self) -> Element:
        return self.__tbl

    @property
    def parent_fig_id(self) -> Optional[str]:
        return self.__entity_meta.get("parent_fig_id", None)

    @property
    def title(self) -> Optional[str]:
        return self.__entity_meta.get("title", None)

    def extract_data_subtbls(self, entity_base: EntityMeta, data: Element) -> Iterator[Entity]:
        tbls = Xpath.elems(data, "./table")
        if len(tbls) == 0:
            return
        elif len(tbls) > 1:
            for ndx, tbl in enumerate(tbls):
                ent = {**entity_base}
                ent["fig_id"] = f"""{ent["fig_id"]}{ndx}"""
                yield from self.__parse(ent, tbl)
        else:
            yield from self.__parse(entity_base, tbls[0])

    def __call__(self) -> Iterator[Entity]:
        # must drive the process from this fn
        ...


ExtractorMap = Dict[str, FigureExtractor]
FigureId = str
ValStr = str


class DocumentParser:
    rgx_fig_id = re_compile(r"Figure\s+(?P<figid>[^\s^:]+).*")
    fig_extractor_overrides: Dict[str, FigureExtractor] = {}

    def __init__(self, doc: Element, spec: str, revision: str):
        self.__doc = doc
        self.__spec = spec
        self.__revision = revision
        self.__post_init__()

    def __post_init__(self) -> None:
        ...

    @property
    def label_overrides(self) -> Dict[Tuple[str, str], str]:
        return {}

    @property
    def brief_overrides(self) -> Dict[Tuple[str, str], str]:
        return {}

    @staticmethod
    def extractor_defaults() -> Dict[str, Type[FigureExtractor]]:
        return {
            "values": ValueTableExtractor,
            "bits": BitsTableExtractor,
            "bytes": BytesTableExtractor,
        }

    @property
    def spec(self) -> str:
        return self.__spec

    @property
    def revision(self) -> str:
        return self.__revision

    @property
    def doc(self) -> Element:
        return self.__doc

    def _on_extract_figure_title(self, tbl: Element) -> Optional[str]:
        """Extract title from figure table."""
        # title = "".join(Xpath.elem_first_req(tbl, "./tr[1]").itertext()).strip()
        fig_tr = Xpath.elem_first(tbl, "./tr[1]")
        assert fig_tr is not None
        title = "".join(fig_tr.itertext()).strip()
        # remove entire tr to simplify downstream processing between top-level and
        # nested figures.
        fig_tr.getparent().remove(fig_tr)
        return title if "Figure" in title else None

    def _on_extract_figure_id(self, tbl: Element, figure_title: str) -> str:
        """Extract figure ID from its title."""
        # Extract figure ID, all figures should have one
        m = self.rgx_fig_id.match(figure_title)
        assert m is not None, f"failed to extract figure ID from {figure_title}"
        return m.group("figid")

    def iter_figures(self) -> Iterator[Tuple[EntityMeta, Element]]:
        for tbl in Xpath.elems(self.doc, "./body/table"):
            # Kludge: should be fixed in source documents, but a few tables
            # (Fig202, Fig223 in Base 2.0c spec) are wrapped in an extra table
            inner_tbl = Xpath.elem_first(tbl, "./tr[1]/td[1]/*[1]")
            if inner_tbl is not None and inner_tbl.tag == "table":
                tbl = inner_tbl

            figure_title = self._on_extract_figure_title(tbl)
            if figure_title is None:
                continue

            figure_id = self._on_extract_figure_id(tbl, figure_title)
            yield {
                "title": figure_title,
                "fig_id": figure_id,
            }, tbl

    def _get_extractor(self, fig_id: str, tbl: Element) -> Optional[Type["FigureExtractor"]]:
        e = self.fig_extractor_overrides.get(fig_id, None)
        if e is not None:
            return e
        # Try to extract and normalize the textual value of the first column
        # This typically says something like 'values', 'bytes' or 'bits' from
        # the tables which we are interested in.
        # (NOTE: works on top-level tables also because we removed the figure tr)
        td1 = Xpath.elem_first(tbl, "./tr[1]/*[1]")
        if td1 is None:
            return None
        td1_txt = "".join(td1.itertext()).lower().strip()
        td1_txt = {
            "byte": "bytes",
            "bit": "bits",
            "value": "values"
        }.get(td1_txt, td1_txt)
        e = self.extractor_defaults().get(td1_txt, None)
        return e  # may be an extractor, may be None

    def _on_parse_fig(self, entity: EntityMeta, tbl: Element) -> Iterator[Entity]:
        """Parse figure, emitting one or more entities.

        NOTE: a figure table may contain nested tables which themselves
              become separate entities. Hence calling this produces an
              iterator of entities."""
        extractor_cls = self._get_extractor(entity["fig_id"], tbl)
        if extractor_cls is None:
            return

        e = extractor_cls(self, entity, tbl, self._on_parse_fig)
        yield from e()

    def parse(self) -> Iterator[EntityMeta]:
        # for each eligible top-level figure
        for entity, tbl in self.iter_figures():
            # ... produce one or more entities (parsed figures)
            # depending on the figure type and whether it contains nested tables.
            yield from self._on_parse_fig(entity, tbl)


class ValueField(TypedDict):
    val: str
    label: str
    brief: NotRequired[str]


class ValueTable(TypedDict):
    title: NotRequired[str]
    parent_fig_id: NotRequired[str]
    fig_id: str
    fields: List[ValueField]


class Range(TypedDict):
    start: int
    end: int


class StructField(TypedDict):
    range: Union[Range, str]
    label: str
    brief: NotRequired[str]


class StructTable(TypedDict):
    title: NotRequired[str]
    parent_fig_id: NotRequired[str]
    fig_id: str
    fields: List[Union["StructTable", StructField]]


# should have way of naming these tables also.
# maybe a map from fig-id to str name
class ValueTableExtractor(FigureExtractor):
    def __call__(self) -> Iterator[Entity]:
        fields: List[ValueField] = []
        for row, val, data in self.rows():
            # val = self.val_clean(row, self.val_extract(row))
            # data_raw: Element = self.data_extract(row)
            value_field: ValueField = {
                "val": self.val_clean(row, val),
                "label": self.data_extract_field_label(row, data),
            }
            brief = self.data_extract_field_brief(row, data)
            if brief is not None:
                value_field["brief"] = brief

            subtbl_ent: EntityMeta = {
                # TODO: change to use value offset instead of field name
                "fig_id": f"""{self.fig_id}_{value_field["label"]}""",
                "parent_fig_id": self.fig_id
            }
            yield from self.extract_data_subtbls(subtbl_ent, data)

            fields.append(value_field)
        yield {
            **self.entity_meta,
            "type": "values",
            "fields": fields
        }

    def rows(self) -> Iterator[Tuple[Element, Element, Element]]:
        # select first td where parent is a tr
        # .. then select the parent (tr) again
        # -> filters out header (th) rows
        # TODO: maybe filter out iterator from try/catch
        for row in Xpath.elems(self.tbl, "./tr/td[1]/parent::tr"):
            try:
                yield row, self.val_extract(row), self.data_extract(row)
            except Exception as e:
                if "".join(row.itertext()).lstrip().lower().startswith("notes:"):
                    continue
                else:
                    raise e

    def val_extract(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, "./td[1]")

    def val_clean(self, row: Element, val_cell: Element) -> str:
        return "".join(val_cell.itertext()).strip().lower()

    def data_extract(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, "./td[2]")

    def data_extract_field_label(self, row: Element, data: Element) -> str:
        p1 = Xpath.elem_first_req(data, "./p[1]")
        txt = "".join(p1.itertext()).strip()
        if txt.lower() == "reserved":
            return "-reserved-"  # TODO: better magic value needed
        txt_parts = txt.split(":", 1)
        if len(txt_parts) == 1:
            return txt
        return txt_parts[0]

    def data_extract_field_brief(self, row: Element, data: Element) -> Optional[str]:
        p1 = Xpath.elem_first_req(data, "./p[1]")
        txt = "".join(p1.itertext()).strip()
        if ":" not in txt:
            return None
        brief = txt.split(":", 1)[1].strip().rstrip(".")
        if len(brief) <= self.BRIEF_MAXLEN:
            return brief
        _brief = brief.split(".", 1)[0]
        return _brief if len(_brief) <= self.BRIEF_MAXLEN else None


class StructTableExtractor(FigureExtractor, ABC):
    rgx_range = re_compile(r"(?P<end>\d+)\s*(:\s*(?P<start>\d+))?")
    rgx_field_lbl = re_compile(r"(\((?P<lbl>[^\)]*)\)\s*:)")

    @property
    @abstractmethod
    def type(self) -> str:
        ...

    def __call__(self) -> Iterator[Entity]:
        fields: List[Union[StructTable, StructField]] = []
        for row, val, data in self.rows():
            val_cleaned: Union[str, Range] = self.val_clean(row, val)
            if isinstance(val_cleaned, dict):  # is range
                override_key = (self.fig_id, str(val_cleaned["start"]))
            else:
                override_key = (self.fig_id, val_cleaned)

            label = self.doc_parser.label_overrides.get(override_key, None)
            if label is None:
                label = self.data_extract_field_label(row, data)

            sfield: StructField = {
                "range": self.val_clean(row, val),
                "label": label
            }

            brief = self.doc_parser.brief_overrides.get(override_key, None)
            if brief is None:
                brief = self.data_extract_field_brief(row, data)

            # no brief override, no brief extracted from table cell
            if brief is not None:
                sfield["brief"] = brief

            subtbl_ent: EntityMeta = {
                # TODO: change to use value offset instead of field name
                "fig_id": f"""{self.fig_id}_{sfield["label"]}""",
                "parent_fig_id": self.fig_id
            }

            yield from self.extract_data_subtbls(subtbl_ent, data)
            fields.append(sfield)

        yield {
            **self.entity_meta,
            "type": self.type,
            "fields": fields
        }

    def rows(self) -> Iterator[Tuple[Element, Element, Element]]:
        # select first td where parent is a tr
        # .. then select the parent (tr) again
        # -> filters out header (th) rows
        # TODO: maybe filter out iterator from try/except
        for row in Xpath.elems(self.tbl, "./tr/td[1]/parent::tr"):
            try:
                yield row, self.val_extract(row), self.data_extract(row)
            except Exception as e:
                row_txt = "".join(row.itertext()).lstrip().lower()
                # TODO: hack - skip notes/... rows.
                if row_txt.startswith("notes:") or row_txt.startswith("…"):
                    continue
                else:
                    breakpoint()
                    raise e

    def val_extract(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, "./td[1]")

    def val_clean(self, row: Element, val_cell: Element) -> Union[str, Range]:
        val = "".join(val_cell.itertext()).strip().lower()
        m = self.rgx_range.match(val)
        if not m:  # cannot parse into a range, sadly
            return val
        end = int(m.group("end"))
        _start = m.group("start")
        start = int(_start) if _start is not None else end
        return {"start": start, "end": end}

    def data_extract(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, "./td[2]")

    def data_extract_field_label(self, row: Element, data: Element) -> str:
        try:
            p1 = Xpath.elem_first_req(data, "./p[1]")
            txt = "".join(p1.itertext()).strip()
            if txt.lower() == "reserved":
                return "-reserved-"  # TODO: better magic value needed
            m = self.rgx_field_lbl.match(txt)
            if m is not None:
                breakpoint()
            txt_parts = txt.split(":", 1)
            if len(txt_parts) == 1:
                return txt
            return txt_parts[0]
        except Exception as e:
            breakpoint()
            raise e

    def data_extract_field_brief(self, row: Element, data: Element) -> Optional[str]:
        # TODO: apply similar for value extraction
        p1_opt = Xpath.elem_first(data, "./p[1]")
        if p1_opt is None:
            return None
        p1 = p1_opt
        txt = "".join(p1.itertext()).strip()
        if ":" not in txt:
            return None
        brief = txt.split(":", 1)[1].strip().rstrip(".")
        if len(brief) <= self.BRIEF_MAXLEN:
            return brief
        _brief = brief.split(".", 1)[0]
        return _brief if len(_brief) <= self.BRIEF_MAXLEN else None


class BitsTableExtractor(StructTableExtractor):
    @property
    def type(self) -> str:
        return "bits"


class BytesTableExtractor(StructTableExtractor):
    @property
    def type(self) -> str:
        return "bytes"


class ZndFig48(StructTableExtractor):
    type = "bytes"

    def data_extract(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, "./td[3]")


class ZndFig50(StructTableExtractor):
    type = "bytes"

    def data_extract(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, "./td[3]")


class NvmCmdSet1c(DocumentParser):
    ...


class NvmCsZoned11c(DocumentParser):

    label_overrides = {
        ("37", "0"): "zt",
        ("37", "1"): "zs",
        ("37", "2"): "za",
    }

    fig_extractor_overrides = {
        "48": ZndFig48,
        "50": ZndFig50,
    }


QuirksMap = Dict[Tuple[str, str], Type[DocumentParser]]


# TODO determine what to return
def parse_document(quirks_map: QuirksMap, spec: Path) -> Entity:
    doc = etree.parse(str(spec.absolute()))

    doc_spec = Xpath.attr_first(doc, "./head/meta/@data-spec")
    doc_rev = Xpath.attr_first(doc, "./head/meta/@data-revision")
    quirks_key = (doc_spec.lower().strip(), doc_rev.lower().strip())
    dp = quirks_map.get(quirks_key, DocumentParser)(doc, doc_spec, doc_rev)
    # TODO: determine exactly what we do here and what we return.
    yield from dp.parse()


# TODO: make configurable, somehow
QUIRKS_MAP: QuirksMap = {
    ("nvm express® nvm command set specification", "1.0c"): NvmCmdSet1c,
    ("nvm express® zoned namespace command set specification", "1.1c"): NvmCsZoned11c
}


@generator
def gen_yidl(scope: Scope):
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    for spec_html in Path(".").glob("*.html"):
        print(f"parsing {spec_html}")
        for e in parse_document(QUIRKS_MAP, spec_html):
            pp.pprint(e)
