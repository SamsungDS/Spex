# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from abc import ABC, abstractmethod
from re import compile as re_compile
from typing import (
    TYPE_CHECKING,
    Any,
    Generator,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
    cast,
)

from spex.jsonspec.defs import (
    ELLIPSIS,
    NOTE,
    OBSOLETE,
    RESERVED,
    SPECIAL_CASE_SET,
    Entity,
    EntityMeta,
    MaybeRange,
    Range,
    StructField,
)
from spex.jsonspec.exceptions import XPathElementNotFoundException
from spex.jsonspec.extractors.figure import FigureExtractor, RowErrPolicy
from spex.jsonspec.extractors.helpers import (
    StructTableMapping,
    content_extract_brief,
    generate_acronym,
    normalize_label,
    validate_label,
)
from spex.jsonspec.extractors.regular_expressions import (
    DYNAMIC_RANGE_REGEX,
    RANGE_REGEX,
    STRUCT_LABEL_REGEX,
)
from spex.jsonspec.lint import LintErr
from spex.jsonspec.queries import contains_th, extract_possible_colspan
from spex.log import logger
from spex.xml import Element, XmlUtils, Xpath

if TYPE_CHECKING:
    from spex.jsonspec.extractors.helpers import Mapping


class StructTableExtractor(FigureExtractor, ABC):
    _col_ndx_range: int
    _col_ndx_content: int
    _col_ndx_label: int

    rgx_range = re_compile(r"(?P<high>\d+)\s*(:\s*(?P<low>\d+))?")

    @staticmethod
    @abstractmethod
    def range_column_hdrs() -> List[str]:
        """Return prioritized list of column headers where extractor should
        extract the row's range.

        The value row is where the extractor will extract the row's range,
        equivalent to the field's offset and width in a C struct.

        Note:
            First match found in figure's actual table headers is used.

            This is intended to be overridden for specialized extractors where the range
            column is using a non-standard heading.
        """
        ...

    def __init__(self, *args: Any, mapping: StructTableMapping, **kwargs: Any):
        super().__init__(*args, **kwargs)
        col_ndxs = {hdr: ndx for ndx, hdr in enumerate(self.tbl_hdrs)}

        self._col_ndx_range = col_ndxs[cast(str, mapping.range_column)]
        self._col_ndx_label = col_ndxs[cast(str, mapping.label_column)]
        self._col_ndx_content = col_ndxs[cast(str, mapping.content_column)]

    @classmethod
    def _can_apply(cls, tbl_col_hdrs: List[str]) -> "Mapping":
        return StructTableMapping(
            range_column=next(
                (hdr for hdr in tbl_col_hdrs if hdr in cls.range_column_hdrs()), None
            ),
            label_column=next(
                (hdr for hdr in tbl_col_hdrs if hdr in cls.label_column_hdrs()), None
            ),
            content_column=next(
                (hdr for hdr in tbl_col_hdrs if hdr in cls.content_column_hdrs()), None
            ),
        )

    @property
    @abstractmethod
    def type(self) -> str: ...

    def _range_to_row_key(self, val: Union[str, Range]) -> str:
        return str(val["low"]) if isinstance(val, dict) else val

    def row_err_handler(
        self,
        row_it: Iterator[Element],
        row: Element,
        fields: List[StructField],
        err: Exception,
    ) -> Generator["Entity", None, RowErrPolicy]:
        """hook called for unhandled errors from extracting a row's value and
        data fields.

        This hook is useful only for individual table overrides to catch special cases.
        """
        if len(Xpath.elems(row, "./td")) == 1:
            # There is only one column in the whole row
            return RowErrPolicy.Continue
        yield from ()  # To turn method into a generator
        return RowErrPolicy.Raise

    def __call__(self) -> Iterator["Entity"]:
        fields: List[StructField] = []
        is_dynamic_table_mode = False
        row_it = self.row_iter()
        for row in row_it:
            if contains_th(row):
                if colspan := extract_possible_colspan(row):
                    # Identify if rows denote a dynamic list table
                    # and set the dynamic mode to true.
                    if "List" in colspan and not is_dynamic_table_mode:
                        is_dynamic_table_mode = True
                # Skip this row, its either the table header or a dynamic list.
                # In any case, it won't result in a StructField
                continue

            # Extract string representations of the fields: range, label and brief
            try:
                range_field, content_field, label_field = self._extract_fields(row)
            except XPathElementNotFoundException as e:
                row_txt = XmlUtils.to_text(row).lower()
                if row_txt.startswith(ELLIPSIS):
                    # revisit ranges here once we have normalized field order
                    # (bits fields are in desc order, bytes are in asc)
                    fields.append(
                        self._struct_field(
                            maybe_range={"low": -1, "high": -1},
                            label=ELLIPSIS,
                        )
                    )
                    continue
                elif row_txt.startswith("note"):
                    break
                else:
                    out = yield from self.row_err_handler(row_it, row, fields, e)
                    if out == RowErrPolicy.Stop:
                        break
                    elif out == RowErrPolicy.Raise:
                        logger.bind(range=XmlUtils.to_text(row).lower()).exception(
                            "failed to parse row"
                        )
                        raise e
                    else:
                        continue
            # If range, label or content is a special case, such as ellipsis,
            # it will need to be handled separately
            if (
                self.is_special_case(range_field)
                or self.is_special_case(label_field)
                or self.is_special_case(content_field)
            ):
                if self.is_special_case(range_field):
                    continue
                elif field := self.handle_special_case(
                    content=content_field,
                    range=self._parse_range(range_field, range_field),
                ):
                    fields.append(field)
                continue

            if is_dynamic_table_mode:
                # Handle subsequent rows if dynamic list table mode is identified
                range = self._parse_dynamic_range(field_range=range_field)
            else:
                range = self._parse_range(range_field, range_field)

            row_key = self._range_to_row_key(range)
            label = self._parse_label(label=label_field, row_key=row_key)
            brief = self._parse_brief(content_field, row_key=row_key)

            sub_table_entity: "EntityMeta" = {
                "fig_id": f"""{self.fig_id}_{row_key}""",
                "parent_fig_id": self.fig_id,
            }

            yield from self.extract_data_sub_table(
                sub_table_entity, self.content_elem(row)
            )
            fields.append(
                self._struct_field(maybe_range=range, label=label, brief=brief)
            )

        # bits tables have their rows in descending order, bytes tables show
        # rows in ascending order this step ensures we are always processing
        # fields sorted by their range in ascending order
        fields = list(reversed(fields)) if self.type == "bits" else fields

        self.validate_fields(fields)

        yield {
            **self.entity_meta,
            "type": self.type,
            "fields": fields,
        }

    def validate_fields(self, fields: List[StructField]) -> None:
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
                prev = prev_range["low"]
                current = field_range["low"]
                if (
                    isinstance(prev, int)
                    and isinstance(current, int)
                    and prev > current
                ):
                    self.add_issue(LintErr.TBL_ROW_ORDER_REVERSED)
                    return
            else:
                prev_range = field_range

        labels = {fields[0]["label"]}
        prev_range = field_get_range(fields[0])

        for field in fields[1:]:
            field_label = field["label"]
            if field_label not in {RESERVED, ELLIPSIS}:
                if field_label in labels:
                    self.add_issue(
                        LintErr.LBL_DUPLICATE,
                        row_key=self._range_to_row_key(field["range"]),
                        ctx={"label": field_label},
                    )
                labels.add(field_label)

            if field_label == "…":
                prev_range = None
                continue

            field_range = field_get_range(field)
            if field_range is not None:
                if prev_range is not None:
                    prev = prev_range["high"]
                    current = field_range["low"]
                    if isinstance(prev, int) and isinstance(current, int):
                        if prev >= current:
                            self.add_issue(
                                LintErr.TBL_FIELD_OVERLAP,
                                row_key=self._range_to_row_key(field_range),
                            )
                        elif prev + 1 != current:
                            self.add_issue(
                                LintErr.TBL_FIELD_GAP,
                                row_key=self._range_to_row_key(field_range),
                            )
                prev_range = field_range
            else:
                # skip next range check
                prev_range = None

    def range_elem(self, row: Element) -> Element:
        """Query row to find range element

        Args:
            row (Element): The row to query

        Returns:
            Element: If label element is found return it, this method can raise
            an XPathElementNotFoundException
        """

        return Xpath.elem_first_req(row, f"./td[{self._col_ndx_range + 1}]")

    def content_elem(self, row: Element) -> Element:
        """Query row to find content element

        Args:
            row (Element): The row to query

        Returns:
            Element: If label element is found return it, this method can raise
            an XPathElementNotFoundException
        """

        return Xpath.elem_first_req(row, f"./td[{self._col_ndx_content + 1}]")

    def label_elem(self, row: Element) -> Element:
        """Query row to find label element

        Args:
            row (Element): The row to query

        Returns:
            Element: If label element is found return it, this method can raise
            an XPathElementNotFoundException
        """
        return Xpath.elem_first_req(row, f"./td[{self._col_ndx_label + 1}]/p[1]")

    def _struct_field(
        self, maybe_range: MaybeRange, label: str, brief: Optional[str] = None
    ) -> StructField:
        if brief:
            return {
                "label": label,
                "range": maybe_range,
                "brief": brief,
            }
        else:
            return {
                "label": label,
                "range": maybe_range,
            }

    def _extract_fields(self, row: Element) -> Tuple[str, str, str]:
        """Extract the range/content/label elements from row

        Will return a tuple containing strings

        Args:
            row (Element): A row element to extract the inner elements of the
            range, label and content columns.

        Returns:
            Tuple[Element, Element]:
              range, label and content
        """
        range = XmlUtils.to_text(self.range_elem(row))
        content = XmlUtils.to_text(self.content_elem(row))
        label = XmlUtils.to_text(self.label_elem(row))
        return (range, content, label)

    def _extract_label_separate_column(self, label: str, row_key: str) -> str:
        txt_parts = label.split(":", 1)
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

    def _extract_label_same_column(self, label: str, row_key: str) -> str:
        match = STRUCT_LABEL_REGEX.regex.match(label)
        if match is None:
            # TODO: This part of the extraction is taken from old implementation.
            # Should be revisited, when time allows
            text_parts = label.split(":", 1)
            label = generate_acronym(text_parts[0])
            self.add_issue(LintErr.LBL_IMPUTED, row_key=row_key)
        elif match.group("acronym") is not None and match.group("acronym") != "":
            label = match.group("acronym")
        elif match.group("label") is not None and match.group("label") != "":
            text = match.group("label")
            if text.upper() in SPECIAL_CASE_SET:
                return text
            label = generate_acronym(text)
            # self.add_issue(LintErr.LBL_IMPUTED, row_key=row_key)
        else:
            self.add_issue(LintErr.LBL_EXTRACT_ERR, row_key=row_key)
        return label

    def _parse_label(self, label: str, row_key: str) -> str:
        try:
            if self._col_ndx_content != self._col_ndx_label:
                label = self._extract_label_separate_column(label, row_key)
            else:
                label = self._extract_label_same_column(label, row_key)
            label = normalize_label(label)
            validate_label(label, self.fig_id, row_key, self.linter)
            return label.lower()
        except Exception as e:
            logger.bind(row=row_key).exception("error extracting label for row")
            raise e

    def _parse_range(self, value: str, row_key: str) -> MaybeRange:
        """Parse text into range if possible with the RANGE_REGEX.

        Args:
            value (str): parameter that contains the range text
            row_key (str): row_key used in case of linting issue

        Returns:
            MaybeRange:
        """
        m = RANGE_REGEX.match(value)
        if not m:  # cannot parse into a range, sadly
            # elided rows are simply skipped.
            self.add_issue(LintErr.RANGE_INVALID, row_key=row_key)
            return value
        else:
            high = int(m.group("high"))
            _low = m.group("low")
            low = int(_low) if _low is not None else high
            if low > high:
                self.add_issue(LintErr.RANGE_REVERSED, row_key=row_key)
            return {"low": low, "high": high}

    def _parse_brief(self, content: str, row_key: str) -> Optional[str]:
        return content_extract_brief(content, self.BRIEF_MAXLEN)

    def _parse_dynamic_range(self, field_range: str) -> MaybeRange:
        range_match = DYNAMIC_RANGE_REGEX.match(
            field_range.replace("\n", "").replace(" ", "")
        )
        if range_match is None:
            self.add_issue(LintErr.RANGE_INVALID, row_key=field_range)
            return field_range
        high, low = range_match.group("low"), range_match.group("high")
        return {"low": low, "high": high}

    @staticmethod
    def is_special_case(content: str) -> bool:
        return content.upper() in SPECIAL_CASE_SET or content.lower().startswith("note")

    def handle_special_case(
        self, content: str, range: MaybeRange
    ) -> Optional[StructField]:
        if content == ELLIPSIS:
            return self._struct_field(
                maybe_range=range,
                label=ELLIPSIS,
            )
        elif content.upper() == RESERVED:
            return self._struct_field(
                maybe_range=range,
                label=RESERVED,
            )
        elif content.upper() == OBSOLETE:
            return self._struct_field(
                maybe_range=range,
                label=OBSOLETE,
            )
        elif content.startswith(NOTE):
            return None

        return None


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
