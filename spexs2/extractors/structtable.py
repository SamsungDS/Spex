from abc import ABC, abstractmethod
from re import compile as re_compile
from typing import Iterator, Union, List, Optional
from spexs2.extractors.figure import FigureExtractor
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
            row_key = str(val_cleaned["low"]) if isinstance(val_cleaned, dict) else val_cleaned
            override_key = (self.fig_id, row_key)

            label = self.doc_parser.label_overrides.get(override_key, None)
            if label is None:
                label = self.data_extract_field_label(row, row_key, data)
            else:
                self.add_issue(Code.L1003, row_key=row_key)

            sfield: StructField = {
                "range": val_cleaned,
                "label": label
            }

            brief = self.doc_parser.brief_overrides.get(override_key, None)
            if brief is None:
                brief = self.data_extract_field_brief(row, row_key, data)

            # no brief override, no brief extracted from table cell
            if brief is not None:
                sfield["brief"] = brief

            subtbl_ent: "EntityMeta" = {
                "fig_id": f"""{self.fig_id}_{row_key}""",
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
        val = "".join(
            e.decode("utf-8") if isinstance(e, bytes) else e
            for e in val_cell.itertext()).strip().lower()
        m = self.rgx_range.match(val)
        if not m:  # cannot parse into a range, sadly
            # elided rows are simply skipped.
            if val != "…":
                self.add_issue(Code.V1002, row_key=val)
            return val
        high = int(m.group("high"))
        _low = m.group("low")
        low = int(_low) if _low is not None else high
        if low > high:
            self.add_issue(Code.V1003, row_key=val)
        return {"low": low, "high": high}

    def data_extract(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, "./td[2]")

    def data_extract_field_label(self, row: Element, row_key: str, data: Element) -> str:
        try:
            p1 = Xpath.elem_first_req(data, "./p[1]")
            txt = "".join(
                e.decode("utf-8") if isinstance(e, bytes) else e
                for e in p1.itertext()).strip()
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
            self.add_issue(Code.L1006, row_key=row_key)
            return gen_name
        except Exception as e:
            breakpoint()
            raise e

    def data_extract_field_brief(self, row: Element, row_key: str, data: Element) -> Optional[str]:
        return data_extract_field_brief(row, data, self.BRIEF_MAXLEN)


class BitsTableExtractor(StructTableExtractor):
    @property
    def type(self) -> str:
        return "bits"


class BytesTableExtractor(StructTableExtractor):
    @property
    def type(self) -> str:
        return "bytes"
