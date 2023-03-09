from typing import TYPE_CHECKING, Iterator, List, Optional, Union, Generator
from spexs2.extractors.figure import FigureExtractor, RowErrPolicy
from spexs2.extractors.helpers import data_extract_field_brief
from spexs2.xml import Xpath, Element
from spexs2.defs import RESERVED, ELLIPSIS, ValueField
from spexs2.lint import Code
from spexs2 import xml  # TODO: for debugging

if TYPE_CHECKING:
    from spexs2.defs import Entity, EntityMeta


class ValueTableExtractor(FigureExtractor):
    @classmethod
    def can_apply(cls, tbl_col_hdrs: List[str]) -> bool:
        return (
            len(set(cls.value_column_hdrs()).intersection(tbl_col_hdrs)) > 0
            and len(set(cls.content_column_hdrs()).intersection(tbl_col_hdrs)) > 0
            and (len(set(cls.label_column_hdrs()).intersection(tbl_col_hdrs))) > 0
        )

    def __call__(self) -> Iterator["Entity"]:
        fields: List[ValueField] = []
        row_it = self.row_iter()
        for row in row_it:
            row_val: Element
            row_data: Element
            try:
                row_val = self.val_extract(row)
                row_data = self.data_extract(row)
            except Exception as e:
                row_txt = "".join(row.itertext()).lstrip().lower()
                if row_txt.startswith(ELLIPSIS):
                    # revisit ranges here once we have normalized field order
                    # (bits fields are in desc order, bytes are in asc)
                    fields.append({"val": ELLIPSIS, "label": ELLIPSIS})
                    continue
                elif row_txt.startswith("notes:"):
                    break
                else:
                    yield from self.row_err_handler(row_it, row, fields, e)
                    # TODO: have to observe the return value
                    continue

            val_cleaned = self.val_clean(row, row_val)
            if val_cleaned == ELLIPSIS:
                fields.append({"val": ELLIPSIS, "label": ELLIPSIS})
                continue

            row_key = str(val_cleaned)

            override_key = (self.fig_id, val_cleaned)
            label = self.doc_parser.label_overrides.get(override_key, None)
            if label is None:
                label = self.data_extract_field_label(row, row_key, row_data)
            else:
                self.add_issue(Code.L1003, row_key=val_cleaned)

            value_field: ValueField = {
                "val": val_cleaned,
                "label": label,
            }

            brief = self.data_extract_field_brief(row, row_key, row_data)
            if brief is not None:
                value_field["brief"] = brief

            subtbl_ent: "EntityMeta" = {
                "fig_id": f"""{self.fig_id}_{str(val_cleaned)}""",
                "parent_fig_id": self.fig_id
            }
            yield from self.extract_data_subtbls(subtbl_ent, row_data)

            fields.append(value_field)

        self.validate_fields(fields)

        yield {
            **self.entity_meta,
            "type": "values",
            "fields": fields
        }

    @staticmethod
    def value_column_hdrs() -> List[str]:
        """Return prioritized list of column headers where extractor should extract the row's value.

        The value row is where the extractor will extract the row's value - loosely equivalent to
        the enum value of the entry.

        Note:
            First match found in figure's actual table headers is used.

            This is intended to be overridden for specialized extractors where the value
            column is using a non-standard heading.
        """
        return ["value"]

    def row_err_handler(self, row_it: Iterator[Element], row: Element,
                        fields: List[ValueField], err: Exception) -> Generator["Entity", None, RowErrPolicy]:
        """hook called for unhandled errors from extracting a row's value and data fields.

        This hook is useful only for individual table overrides to catch special cases."""
        yield from ()  # To turn method into a generator
        return RowErrPolicy.Raise

    def _val_to_rowkey(self, val: Union[str, int]) -> str:
        return str(val)

    def validate_fields(self, fields: List[ValueField]):
        if len(fields) < 2:
            return

        lbls = set()
        vals = set()

        for field in fields:
            fval = field["val"]
            flbl = field["label"]

            if flbl in {RESERVED, ELLIPSIS}:
                continue

            if flbl in lbls:
                self.add_issue(Code.T1003, row_key=self._val_to_rowkey(fval))
            lbls.add(flbl)

            if fval in vals:
                self.add_issue(Code.T1005, row_key=self._val_to_rowkey(fval))
            vals.add(fval)

    def val_extract(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, "./td[1]")

    def val_clean(self, row: Element, val_cell: Element) -> Union[str, int]:
        # TODO: read as number if possible, complain if not a hex value using the 'h' suffix
        return "".join(
            e.decode("utf-8") if isinstance(e, bytes) else e
            for e in val_cell.itertext()).strip().lower()

    def data_extract(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, "./td[2]")

    def data_extract_field_label(self, row: Element, row_key: str, data: Element) -> str:
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
            self.add_issue(Code.L1003, row_key=row_key)
        # generic naming strategy
        return txt_parts[0].replace(" ", "_").upper()

    def data_extract_field_brief(self, row: Element, row_key: str, data: Element) -> Optional[str]:
        return data_extract_field_brief(row, data, self.BRIEF_MAXLEN)
