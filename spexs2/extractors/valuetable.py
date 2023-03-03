from typing import TYPE_CHECKING, Iterator, List, Optional
from spexs2.extractors.figure import FigureExtractor, RowResult
from spexs2.extractors.helpers import data_extract_field_brief
from spexs2.xml import Xpath, Element
from spexs2.defs import RESERVED
from spexs2 import xml  # TODO: for debugging

if TYPE_CHECKING:
    from spexs2.defs import Entity, ValueField, EntityMeta


class ValueTableExtractor(FigureExtractor):
    def __call__(self) -> Iterator["Entity"]:
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

            subtbl_ent: "EntityMeta" = {
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
            return RESERVED
        txt_parts = txt.split(":", 1)
        # generic naming strategy
        return txt_parts[0].replace(" ", "_").upper()

    def data_extract_field_brief(self, row: Element, data: Element) -> Optional[str]:
        return data_extract_field_brief(row, data, self.BRIEF_MAXLEN)
