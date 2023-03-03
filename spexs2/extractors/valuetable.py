from typing import TYPE_CHECKING, Iterator, List, Optional, Union
from spexs2.extractors.figure import FigureExtractor
from spexs2.extractors.helpers import data_extract_field_brief
from spexs2.xml import Xpath, Element
from spexs2.defs import RESERVED
from spexs2.lint import Code
from spexs2 import xml  # TODO: for debugging

if TYPE_CHECKING:
    from spexs2.defs import Entity, ValueField, EntityMeta


class ValueTableExtractor(FigureExtractor):
    def __call__(self) -> Iterator["Entity"]:
        fields: List[ValueField] = []
        for row, val, data in self.rows():
            val_cleaned: Union[str, int] = self.val_clean(row, val)
            if val_cleaned == "…":
                # skip these filler rows
                continue

            override_key = (self.fig_id, val_cleaned)
            label = self.doc_parser.label_overrides.get(override_key, None)
            if label is None:
                label = self.data_extract_field_label(row, data)

            value_field: ValueField = {
                "val": val_cleaned,
                "label": label,
            }

            brief = self.data_extract_field_brief(row, data)
            if brief is not None:
                value_field["brief"] = brief

            subtbl_ent: "EntityMeta" = {
                "fig_id": f"""{self.fig_id}_{str(val_cleaned)}""",
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

    def val_clean(self, row: Element, val_cell: Element) -> Union[str, int]:
        # TODO: read as number if possible, complain if not a hex value using the 'h' suffix
        return "".join(
            e.decode("utf-8") if isinstance(e, bytes) else e
            for e in val_cell.itertext()).strip().lower()

    def data_extract(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, "./td[2]")

    def data_extract_field_label(self, row: Element, data: Element) -> str:
        p1 = Xpath.elem_first_req(data, "./p[1]")
        txt = "".join(
            e.decode("utf-8") if isinstance(e, bytes) else e for e in p1.itertext()).strip()
        if txt.lower() == "reserved":
            return RESERVED
        txt_parts = txt.split(":", 1)
        if txt_parts[0] == txt_parts:
            # to infer labels, we need the text to be of the form
            # 'Foo Bar Baz: lorem ipsum...' - if no colon is found, this is
            # not the case, ergo we cannot reliably extract a label.
            # TODO: fix, must have the cleaned value here, for reporting
            self.add_issue(Code.L1003, row=row)
        # generic naming strategy
        return txt_parts[0].replace(" ", "_").upper()

    def data_extract_field_brief(self, row: Element, data: Element) -> Optional[str]:
        return data_extract_field_brief(row, data, self.BRIEF_MAXLEN)
