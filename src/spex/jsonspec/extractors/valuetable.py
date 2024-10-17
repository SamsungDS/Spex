# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import replace as dataclass_replace
from typing import TYPE_CHECKING, Any, Generator, Iterator, List, Optional, Union, cast

from spex.jsonspec.defs import ELLIPSIS, RESERVED, ValueField
from spex.jsonspec.exceptions import LabelExtractionError
from spex.jsonspec.extractors.figure import FigureExtractor, RowErrPolicy
from spex.jsonspec.extractors.helpers import (
    ValueTableMapping,
    content_extract_brief,
    extract_content,
    mapping_incomplete,
    normalize_label,
    rearrange_num_label,
    validate_label,
)
from spex.jsonspec.extractors.regular_expressions import VALUE_LABEL_REGEX
from spex.jsonspec.lint import LintErr
from spex.jsonspec.queries import contains_th
from spex.xml import Element, XmlUtils, Xpath

if TYPE_CHECKING:
    from spex.jsonspec.defs import Entity, EntityMeta
    from spex.jsonspec.extractors.helpers import Mapping


class ValueTableExtractor(FigureExtractor):
    _col_ndx_value: int
    _col_ndx_content: int
    _col_ndx_label: int

    @classmethod
    def _can_apply(cls, tbl_col_hdrs: List[str]) -> "Mapping":
        m = ValueTableMapping(
            value_column=next(
                (hdr for hdr in tbl_col_hdrs if hdr in cls.value_column_hdrs()), None
            ),
            label_column=next(
                (hdr for hdr in tbl_col_hdrs if hdr in cls.label_column_hdrs()), None
            ),
            content_column=next(
                (hdr for hdr in tbl_col_hdrs if hdr in cls.content_column_hdrs()), None
            ),
        )
        if not mapping_incomplete(m):
            return m
        if len(tbl_col_hdrs) == 2 and m.value_column == "value":
            other_col = next((hdr for hdr in tbl_col_hdrs if hdr != "value"), None)
            if other_col:
                return dataclass_replace(
                    m, label_column=other_col, content_column=other_col
                )

        # no other avenue, fail
        return m

    def __init__(self, *args: Any, mapping: ValueTableMapping, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        col_ndxs = {hdr: ndx for ndx, hdr in enumerate(self.tbl_hdrs)}

        self._col_ndx_value = col_ndxs[cast(str, mapping.value_column)]
        self._col_ndx_label = col_ndxs[cast(str, mapping.label_column)]
        self._col_ndx_content = col_ndxs[cast(str, mapping.content_column)]

    def __call__(self) -> Iterator["Entity"]:
        fields: List[ValueField] = []
        row_it = self.row_iter()
        for row in row_it:
            row_val: Element
            row_data: Element
            if contains_th(row):
                # Skip this row, its the table header.
                # In any case, it is handled before getting here.
                continue
            try:
                row_val = self.val_elem(row)
                row_data = self.content_elem(row)
            except Exception as e:
                row_txt = XmlUtils.to_text(row).lower()
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

            override_key = (self.fig_id, str(val_cleaned))
            label = self.doc_parser.label_overrides.get(override_key, None)
            if label is None:
                label = self._extract_label(row, row_key, row_data)
            else:
                self.add_issue(LintErr.LBL_OVERRIDDEN, row_key=str(val_cleaned))

            value_field: ValueField = {
                "val": val_cleaned,
                "label": label,
            }

            brief = self._content_extract_brief(row, row_key, row_data)
            if brief is not None:
                value_field["brief"] = brief

            subtbl_ent: "EntityMeta" = {
                "fig_id": f"""{self.fig_id}_{str(val_cleaned)}""",
                "parent_fig_id": self.fig_id,
            }
            yield from self.extract_data_sub_table(subtbl_ent, row_data)

            fields.append(value_field)

        self.validate_fields(fields)

        yield {**self.entity_meta, "fields": fields, "type": "values"}

    @staticmethod
    def value_column_hdrs() -> List[str]:
        """Return prioritized list of column headers where extractor should
        extract the row's value.

        The value row is where the extractor will extract the row's value -
        loosely equivalent to the enum value of the entry.

        Note:
            First match found in figure's actual table headers is used.

            This is intended to be overridden for specialized extractors where
            the value column is using a non-standard heading.
        """
        return ["value", "values"]

    @staticmethod
    def content_column_hdrs() -> List[str]:
        """Return prioritized list of column headers where extractor should
        extract the row's content.

        The content row is where the extractor will extract a brief (short
        documentation string) for the row and any sub-tables, if present.
        Also, if there is no dedicated column for row names, these too will be
        extracted from this column.

        Note:
            First match found in figure's actual table headers is used.

            This is intended to be overridden for specialized extractors where
            the content column is using a non-standard heading.
        """
        return ["definition", "description", "power scope"]

    @staticmethod
    def label_column_hdrs() -> List[str]:
        """Return prioritized list of column headers where extractor should
        extract the row's name.

        Note:
            First match found in figure's actual table headers is used.

            This is intended to be overridden for specialized extractors where the label
            column is using a non-standard heading.
        """
        return ["attribute", "definition", "description", "power scope"]

    def row_err_handler(
        self,
        row_it: Iterator[Element],
        row: Element,
        fields: List[ValueField],
        err: Exception,
    ) -> Generator["Entity", None, RowErrPolicy]:
        """hook called for unhandled errors from extracting a row's value and
        data fields.

        This hook is useful only for individual table overrides to catch special cases.
        """
        yield from ()  # To turn method into a generator
        return RowErrPolicy.Raise

    def _val_to_rowkey(self, val: Union[str, int]) -> str:
        return str(val)

    def validate_fields(self, fields: List[ValueField]) -> None:
        if len(fields) < 2:
            return

        labels = set()
        values = set()

        for field in fields:
            field_value = field["val"]
            field_label = field["label"]

            if field_label in {RESERVED, ELLIPSIS}:
                continue

            if field_label in labels:
                self.add_issue(
                    LintErr.LBL_DUPLICATE,
                    row_key=self._val_to_rowkey(field_value),
                    ctx={"label": field_label},
                )
            labels.add(field_label)

            if field_value in values:
                self.add_issue(
                    LintErr.VAL_DUPLICATE, row_key=self._val_to_rowkey(field_value)
                )
            values.add(field_value)

    def val_elem(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, f"./td[{self._col_ndx_value + 1}]")

    def val_clean(self, row: Element, val_cell: Element) -> Union[str, int]:
        return XmlUtils.to_text(val_cell).lower()

    def content_elem(self, row: Element) -> Element:
        return Xpath.elem_first_req(row, f"./td[{self._col_ndx_content + 1}]")

    def _extract_label_dedicated_col(self, row: Element, row_key: str) -> str:
        # if we hit this, some document actually has a value table with a
        # dedicated 'attribute' column
        p1 = Xpath.elem_first_req(row, f"./td[{self._col_ndx_label + 1}]/p[1]")
        txt = XmlUtils.to_text(p1).lower()
        if txt == "reserved":
            return RESERVED

        txt_parts = txt.split(":", 1)
        if len(txt_parts) == 1:
            # no explicit name, forced to infer it
            self.add_issue(LintErr.LBL_IMPUTED, fig=self.fig_id, row_key=row_key)
        else:
            # if we hit this, some figure actually has a dedicated attribute
            # column where the text contains a an explicitly-given short-hand/label
            pass
        return txt_parts[0].replace(" ", "_").upper()

    def _extract_label(self, row: Element, row_key: str, data: Element) -> str:
        if self._col_ndx_content != self._col_ndx_label:
            label = self._extract_label_dedicated_col(row, row_key)
            if label.upper() == RESERVED:
                return RESERVED
        else:
            text: Optional[str] = extract_content(data)
            if text is None:
                self.add_issue(LintErr.LBL_EXTRACT_ERR, row_key=row_key)
                raise LabelExtractionError("Could not extract label")
            if text.upper() == RESERVED:
                return RESERVED
            match = VALUE_LABEL_REGEX.regex.match(text)
            if match is None:
                self.add_issue(LintErr.LBL_EXTRACT_ERR, row_key=row_key)
                label = text
            elif match.group("label") is not None and match.group("label") != "":
                label = match.group("label")
            else:
                self.add_issue(LintErr.LBL_EXTRACT_ERR, row_key=row_key)
                label = text
        label = rearrange_num_label(label)
        label = normalize_label(label)
        validate_label(label, self.fig_id, row_key, self.linter)
        return label

    def _content_extract_brief(
        self, row: Element, row_key: str, data: Element
    ) -> Optional[str]:
        content = self.content_elem(row)
        return content_extract_brief(XmlUtils.to_text(content), self.BRIEF_MAXLEN)
