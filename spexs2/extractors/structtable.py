from abc import ABC, abstractmethod
from re import compile as re_compile
from typing import TYPE_CHECKING, Iterator, Tuple, Union, Optional, List
from spexs2.extractors.figure import FigureExtractor
from spexs2.extractors.helpers import data_extract_field_brief
from spexs2.xml import Element, Xpath
from spexs2.defs import RESERVED
from spexs2 import xml  # TODO: for debugging


if TYPE_CHECKING:
    from spexs2.defs import Entity, EntityMeta, Range, StructField, StructTable


class StructTableExtractor(FigureExtractor, ABC):
    rgx_range = re_compile(r"(?P<end>\d+)\s*(:\s*(?P<start>\d+))?")
    rgx_field_lbl = re_compile(r"^.*\s+(\((?P<lbl>[^\)]*)\)\s*:)")

    @property
    @abstractmethod
    def type(self) -> str:
        ...

    def __call__(self) -> Iterator["Entity"]:
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

            subtbl_ent: "EntityMeta" = {
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

    def val_clean(self, row: Element, val_cell: Element) -> Union[str, "Range"]:
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
                return RESERVED
            m = self.rgx_field_lbl.match(txt)
            if m is not None:
                return m.group("lbl").replace(" ", "").lower()
            txt_parts = txt.split(":", 1)
            # generic naming strategy
            # TODO: improve, replace certain words/sentences by certain abbreviations
            #       namespace -> ns, pointer -> ptr
            gen_name = "".join(w[0] for w in txt_parts[0].split()).lower()
            return gen_name
        except Exception as e:
            breakpoint()
            raise e

    def data_extract_field_brief(self, row: Element, data: Element) -> Optional[str]:
        return data_extract_field_brief(row, data, self.BRIEF_MAXLEN)


class BitsTableExtractor(StructTableExtractor):
    @property
    def type(self) -> str:
        return "bits"


class BytesTableExtractor(StructTableExtractor):
    @property
    def type(self) -> str:
        return "bytes"
