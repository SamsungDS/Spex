from abc import ABC, abstractmethod
from re import compile as re_compile
from typing import Iterator, Union, List, Optional, Generator
from spexs2.extractors.figure import FigureExtractor, RowErrPolicy
from spexs2.extractors.helpers import data_extract_field_brief
from spexs2.xml import Element, Xpath
from spexs2.defs import RESERVED, ELLIPSIS, Entity, EntityMeta, Range, StructField
from spexs2.lint import Code
from spexs2 import xml  # TODO: for debugging


class StructTableExtractor(FigureExtractor, ABC):
    rgx_range = re_compile(r"(?P<high>\d+)\s*(:\s*(?P<low>\d+))?")
    rgx_field_lbl = re_compile(r"^.*\s+(\((?P<lbl>[^\)]*)\)\s*:)")

    @property
    @abstractmethod
    def type(self) -> str:
        ...

    def _range_to_rowkey(self, val: Union[str, Range]) -> str:
        return str(val["low"]) if isinstance(val, dict) else val

    def row_err_handler(self, row_it: Iterator[Element], row: Element,
                        fields: List[StructField], err: Exception) -> Generator["Entity", None, RowErrPolicy]:
        """hook called for unhandled errors from extracting a row's value and data fields.

        This hook is useful only for individual table overrides to catch special cases."""
        yield from ()  # To turn method into a generator
        return RowErrPolicy.Raise

    def __call__(self) -> Iterator["Entity"]:
        fields: List[StructField] = []
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
                    fields.append({"range": {"low": -1, "high": -1}, "label": ELLIPSIS})
                    continue
                elif row_txt.startswith("notes:"):
                    break
                else:
                    yield from self.row_err_handler(row_it, row, fields, e)
                    # TODO: have to observe the return value
                    continue

            val_cleaned = self.val_clean(row, row_val)
            if val_cleaned == ELLIPSIS:
                fields.append({
                    "range": {"low": -1, "high": -1},
                    "label": ELLIPSIS
                })
                continue

            row_key = self._range_to_rowkey(val_cleaned)
            override_key = (self.fig_id, row_key)

            label = self.doc_parser.label_overrides.get(override_key, None)
            if label is None:
                label = self.data_extract_field_label(row, row_key, row_data)
            else:
                self.add_issue(Code.L1003, row_key=row_key)

            sfield: StructField = {
                "range": val_cleaned,
                "label": label
            }

            brief = self.doc_parser.brief_overrides.get(override_key, None)
            if brief is None:
                brief = self.data_extract_field_brief(row, row_key, row_data)

            # no brief override, no brief extracted from table cell
            if brief is not None:
                sfield["brief"] = brief

            subtbl_ent: "EntityMeta" = {
                "fig_id": f"""{self.fig_id}_{row_key}""",
                "parent_fig_id": self.fig_id
            }

            yield from self.extract_data_subtbls(subtbl_ent, row_data)
            fields.append(sfield)

        # bits tables have their rows in descending order, bytes tables show rows in ascending order
        # this step ensures we are always processing fields sorted by their range in ascending order
        fields = list(reversed(fields)) if self.type == "bits" else fields

        # TODO: patch '...' row ranges to fit surrounding fields.
        self.validate_fields(fields)

        yield {
            **self.entity_meta,
            "type": self.type,
            "fields": fields
        }

    def validate_fields(self, fields: List[StructField]):
        if len(fields) < 2:
            return

        # Check whether row order is wrong for the table
        prev_range = fields[0]["range"]
        for field_range in (f["range"] for f in fields):
            if not isinstance(field_range, dict):
                prev_range = None
                continue
            elif isinstance(prev_range, dict):
                if prev_range["low"] > field_range["low"]:
                    self.add_issue(Code.T1004)
                    return

        lbls = {fields[0]["label"]}
        prev_range = fields[0]["range"] if isinstance(fields[0]["range"], dict) else None

        for field in fields[1:]:
            flbl = field["label"]
            if flbl not in {RESERVED, ELLIPSIS}:
                if flbl in lbls:
                    self.add_issue(Code.T1003, row_key=self._range_to_rowkey(field["range"]))
                lbls.add(flbl)

            if flbl == "…":
                prev_range = None
                continue

            if isinstance(field_range := field["range"], dict):
                if prev_range is not None:
                    if prev_range["high"] >= field_range["low"]:
                        self.add_issue(Code.T1001, row_key=self._range_to_rowkey(field_range))
                    elif prev_range["high"] + 1 != field_range["low"]:
                        self.add_issue(Code.T1002, row_key=self._range_to_rowkey(field_range))
                prev_range = field_range
            else:
                # skip next range check
                prev_range = None

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
