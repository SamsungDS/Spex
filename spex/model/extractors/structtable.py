from abc import ABC, abstractmethod
from re import compile as re_compile
from typing import Iterator, Union, List, Optional, Generator, Dict
from spex.model.extractors.figure import FigureExtractor, RowErrPolicy
from spex.model.extractors.helpers import content_extract_brief, validate_label
from spex.xml import Element, Xpath, XmlUtils
from spex.model.defs import RESERVED, ELLIPSIS, Entity, EntityMeta, Range, StructField
from spex.model.lint import LintErr


class StructTableExtractor(FigureExtractor, ABC):
    _col_ndx_range: int
    _col_ndx_content: int
    _col_ndx_label: int

    rgx_range = re_compile(r"(?P<high>\d+)\s*(:\s*(?P<low>\d+))?")
    rgx_field_lbl = re_compile(r"^.*\s+(\((?P<lbl>[^\)]*)\)\s*:)")

    @staticmethod
    @abstractmethod
    def range_column_hdrs() -> List[str]:
        """Return prioritized list of column headers where extractor should extract the row's range.

        The value row is where the extractor will extract the row's range, equivalent to the field's
        offset and width in a C struct.

        Note:
            First match found in figure's actual table headers is used.

            This is intended to be overridden for specialized extractors where the range
            column is using a non-standard heading.
        """
        ...

    def _get_col_ndx(self, col_hdrs: List[str], tbl_cols_ndxs: Dict[str, int]) -> int:
        for colname in col_hdrs:
            ndx = tbl_cols_ndxs.get(colname, None)
            if ndx is not None:
                return ndx
        raise RuntimeError("failed to find column to extract ranges from")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        col_ndxs = {hdr: ndx for ndx, hdr in enumerate(self.tbl_hdrs)}
        self._col_ndx_range = self._get_col_ndx(self.range_column_hdrs(), col_ndxs)
        self._col_ndx_content = self._get_col_ndx(self.content_column_hdrs(), col_ndxs)
        self._col_ndx_label = self._get_col_ndx(self.label_column_hdrs(), col_ndxs)

    @classmethod
    def can_apply(cls, tbl_col_hdrs: List[str]) -> bool:
        return (
            len(set(cls.range_column_hdrs()).intersection(tbl_col_hdrs)) > 0
            and len(set(cls.content_column_hdrs()).intersection(tbl_col_hdrs)) > 0
            and (len(set(cls.label_column_hdrs()).intersection(tbl_col_hdrs))) > 0
        )

    @property
    @abstractmethod
    def type(self) -> str:
        ...

    def _range_to_rowkey(self, val: Union[str, Range]) -> str:
        return str(val["low"]) if isinstance(val, dict) else val

    def row_err_handler(
        self,
        row_it: Iterator[Element],
        row: Element,
        fields: List[StructField],
        err: Exception,
    ) -> Generator["Entity", None, RowErrPolicy]:
        """hook called for unhandled errors from extracting a row's value and data fields.

        This hook is useful only for individual table overrides to catch special cases.
        """
        yield from ()  # To turn method into a generator
        return RowErrPolicy.Raise

    def __call__(self) -> Iterator["Entity"]:
        fields: List[StructField] = []
        row_it = self.row_iter()
        for row in row_it:
            row_range: Element
            row_data: Element
            try:
                row_range = self.range_elem(row)
                row_data = self.content_elem(row)
            except Exception as e:
                row_txt = XmlUtils.to_text(row).lower()
                if row_txt.startswith(ELLIPSIS):
                    # revisit ranges here once we have normalized field order
                    # (bits fields are in desc order, bytes are in asc)
                    fields.append({"range": {"low": -1, "high": -1}, "label": ELLIPSIS})
                    continue
                elif row_txt.startswith("notes:"):
                    break
                else:
                    out = yield from self.row_err_handler(row_it, row, fields, e)
                    if out == RowErrPolicy.Stop:
                        break
                    elif out == RowErrPolicy.Raise:
                        raise e
                    else:
                        continue

            range = self.range_clean(row, row_range)
            if range == ELLIPSIS:
                fields.append({"range": {"low": -1, "high": -1}, "label": ELLIPSIS})
                continue

            row_key = self._range_to_rowkey(range)
            override_key = (self.fig_id, row_key)

            label = self.doc_parser.label_overrides.get(override_key, None)
            if label is None:
                label = self._extract_label(row, row_key, row_data)
            else:
                self.add_issue(LintErr.LBL_IMPUTED, row_key=row_key)

            sfield: StructField = {"range": range, "label": label}

            brief = self.doc_parser.brief_overrides.get(override_key, None)
            if brief is None:
                brief = self._content_extract_brief(row, row_key, row_data)

            # no brief override, no brief extracted from table cell
            if brief is not None:
                sfield["brief"] = brief

            subtbl_ent: "EntityMeta" = {
                "fig_id": f"""{self.fig_id}_{row_key}""",
                "parent_fig_id": self.fig_id,
            }

            yield from self.extract_data_subtbls(subtbl_ent, row_data)
            fields.append(sfield)

        # bits tables have their rows in descending order, bytes tables show rows in ascending order
        # this step ensures we are always processing fields sorted by their range in ascending order
        fields = list(reversed(fields)) if self.type == "bits" else fields

        self.validate_fields(fields)

        yield {
            # https://github.com/python/mypy/issues/4122#issuecomment-336924377
            **self.entity_meta,  # type: ignore
            "type": self.type,
            "fields": fields,
        }

    def validate_fields(self, fields: List[StructField]):
        if len(fields) < 2:
            return

        def field_get_range(f: StructField) -> Optional[Range]:
            if f["label"] == ELLIPSIS or isinstance(f["range"], str):
                return None
            return f["range"]

        # Check whether row order is wrong for the table
        prev_range: Optional[Range] = field_get_range(fields[0])
        for field in fields:
            field_range = field_get_range(field)
            if field_range is None:
                prev_range = None
                continue
            elif prev_range is not None:
                if prev_range["low"] > field_range["low"]:
                    if self.fig_id == "94":
                        breakpoint()
                    self.add_issue(LintErr.TBL_ROW_ORDER_REVERSED)
                    return
            else:
                prev_range = field_range

        lbls = {fields[0]["label"]}
        prev_range = field_get_range(fields[0])

        for field in fields[1:]:
            flbl = field["label"]
            if flbl not in {RESERVED, ELLIPSIS}:
                if flbl in lbls:
                    self.add_issue(
                        LintErr.LBL_DUPLICATE,
                        row_key=self._range_to_rowkey(field["range"]),
                        ctx={"label": flbl},
                    )
                lbls.add(flbl)

            if flbl == "…":
                prev_range = None
                continue

            field_range = field_get_range(field)
            if field_range is not None:
                if prev_range is not None:
                    if prev_range["high"] >= field_range["low"]:
                        self.add_issue(
                            LintErr.TBL_FIELD_OVERLAP,
                            row_key=self._range_to_rowkey(field_range),
                        )
                    elif prev_range["high"] + 1 != field_range["low"]:
                        self.add_issue(
                            LintErr.TBL_FIELD_GAP,
                            row_key=self._range_to_rowkey(field_range),
                        )
                prev_range = field_range
            else:
                # skip next range check
                prev_range = None

    def range_elem(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, f"./td[{self._col_ndx_range + 1}]")

    def range_clean(self, row: Element, val_cell: Element) -> Union[str, "Range"]:
        val = (
            "".join(
                e.decode("utf-8") if isinstance(e, bytes) else e
                for e in val_cell.itertext()
            )
            .strip()
            .lower()
        )
        m = self.rgx_range.match(val)
        if not m:  # cannot parse into a range, sadly
            # elided rows are simply skipped.
            if val != "…":
                self.add_issue(LintErr.RANGE_INVALID, row_key=val)
            return val
        high = int(m.group("high"))
        _low = m.group("low")
        low = int(_low) if _low is not None else high
        if low > high:
            self.add_issue(LintErr.RANGE_REVERSED, row_key=val)
        return {"low": low, "high": high}

    def content_elem(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, f"./td[{self._col_ndx_content + 1}]")

    def _extract_label_separate_col(self, row: Element, row_key: str) -> str:
        p1 = Xpath.elem_first_req(row, f"./td[{self._col_ndx_label + 1}]/p[1]")
        txt = XmlUtils.to_text(p1).lower()
        if txt == "reserved":
            return RESERVED

        txt_parts = txt.split(":", 1)
        if len(txt_parts) == 1:
            # no explicit name, forced to infer it
            self.add_issue(LintErr.LBL_IMPUTED, fig=self.fig_id, row_key=row_key)
            return "".join(w[0] for w in txt_parts[0].split())
        else:
            if " " in txt_parts[0]:
                self.add_issue(
                    LintErr.LBL_INVALID_CHRS, fig=self.fig_id, row_key=row_key
                )
            return txt_parts[0]

    def _extract_label(self, row: Element, row_key: str, data: Element) -> str:
        if self._col_ndx_content != self._col_ndx_label:
            lbl = self._extract_label_separate_col(row, row_key)
            if lbl == RESERVED:
                return RESERVED
        else:
            p1 = Xpath.elem_first_req(data, "./p[1]")
            txt = XmlUtils.to_text(p1)
            if txt.lower() == "reserved":
                return RESERVED
            m = self.rgx_field_lbl.match(txt)
            if m is not None:
                lbl = m.group("lbl").replace(" ", "").lower()
                validate_label(lbl, self.fig_id, row_key, self.linter)
                return lbl
            txt_parts = txt.split(":", 1)
            # generic naming strategy
            # TODO: improve, replace certain words/sentences by certain abbreviations
            #       namespace -> ns, pointer -> ptr
            gen_name = "".join(w[0] for w in txt_parts[0].split()).lower()
            self.add_issue(LintErr.LBL_IMPUTED, row_key=row_key)
            lbl = gen_name
        validate_label(lbl, self.fig_id, row_key, self.linter)
        return lbl

    def _content_extract_brief(
        self, row: Element, row_key: str, data: Element
    ) -> Optional[str]:
        return content_extract_brief(row, data, self.BRIEF_MAXLEN)


class BitsTableExtractor(StructTableExtractor):
    @staticmethod
    def range_column_hdrs() -> List[str]:
        return ["bits"]

    @property
    def type(self) -> str:
        return "bits"


class BytesTableExtractor(StructTableExtractor):
    @staticmethod
    def range_column_hdrs() -> List[str]:
        return ["bytes"]

    @property
    def type(self) -> str:
        return "bytes"
