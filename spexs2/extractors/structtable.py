from abc import ABC, abstractmethod
from re import compile as re_compile
from typing import Iterator, Tuple, Union, List, Optional
from spexs2.extractors.figure import FigureExtractor, RowResult
from spexs2.extractors.helpers import data_extract_field_brief
from spexs2.xml import Element, Xpath
from spexs2.defs import RESERVED, Entity, EntityMeta, Range, StructField, StructTable
from spexs2.lint import Code
from spexs2 import xml  # TODO: for debugging


class StructTableExtractor(FigureExtractor, ABC):
    rgx_range = re_compile(r"(?P<high>\d+)\s*(:\s*(?P<low>\d+))?")
    rgx_field_lbl = re_compile(r"^.*\s+(\((?P<lbl>[^\)]*)\)\s*:)")

    @property
    @abstractmethod
    def type(self) -> str:
        ...

    def __call__(self) -> Iterator["Entity"]:
        fields: List[Union[StructTable, StructField]] = []
        for row, val, data in self.rows():
            val_cleaned: Union[str, Range] = self.val_clean(row, val)
            if val_cleaned == "…":
                # skip these filler rows
                continue
            if isinstance(val_cleaned, dict):  # is range
                override_key = (self.fig_id, str(val_cleaned["low"]))
            else:
                override_key = (self.fig_id, val_cleaned)

            label = self.doc_parser.label_overrides.get(override_key, None)
            if label is None:
                label = self.data_extract_field_label(row, data)

            sfield: StructField = {
                "range": val_cleaned,
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

    def val_extract(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, "./td[1]")

    def val_clean(self, row: Element, val_cell: Element) -> Union[str, "Range"]:
        val = "".join(val_cell.itertext()).strip().lower()
        m = self.rgx_range.match(val)
        if not m:  # cannot parse into a range, sadly
            # elided rows are simply skipped.
            if val != "…":
                self.add_issue(Code.V1002, row=val)
            return val
        high = int(m.group("high"))
        _low = m.group("low")
        low = int(_low) if _low is not None else high
        if low > high:
            self.add_issue(Code.V1003, row=val)
        return {"low": low, "high": high}

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
