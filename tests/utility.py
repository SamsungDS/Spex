# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause
import json
import re
from pathlib import Path
from typing import Callable, List

import pytest

from spex.jsonspec.defs import JSON, EntityMeta
from spex.jsonspec.lint import LintErr
from spex.jsonspec.parse import html_to_spec_doc
from spex.jsonspec.parserargs import ParserArgs


class LintException(RuntimeError):
    def __init__(
        self, message: object, lint_errors: JSON, entities: List[EntityMeta]
    ) -> None:
        super().__init__(message)
        self.lint_errors = lint_errors
        self.entities = entities


@pytest.fixture
def html_parser(
    tmp_path_factory: pytest.TempPathFactory,
) -> Callable[[str, bool], List[EntityMeta]]:
    """Fixture that returns a function for parsing html

    This fixture can be used to parse html into json using the spex parser
    it will return a list of Entities that can be used to validate the result.

    If a linting error is encountered it will raise an LintException.

    Args:
        tmp_path_factory (pytest.TempPathFactory): Builtin pytest tmp path
        fixture, is used to temporary persist output to disk.

    Returns:
        Callable[[str], List[EntityMeta]]: Function that parses a html string
    """

    def parse_inner(content: str, strict: bool = False) -> List[EntityMeta]:
        spec_doc = html_to_spec_doc(content)

        output_dir = tmp_path_factory.mktemp("output")
        args = ParserArgs(output_dir=output_dir)

        document_parser = spec_doc.get_parser(args)
        entities = [entity for entity in document_parser.parse()]
        reported_lint_errs = [
            lint_entry.to_json()
            for lint_entry in document_parser.linter.lint_entries()
            if strict or lint_entry.err == LintErr.TBL_SKIPPED
        ]
        if len(reported_lint_errs):
            raise LintException(
                "HTML Parsing resulted in linting errors:\n"
                f" {json.dumps(reported_lint_errs, indent=2)}"
                f" {json.dumps(entities, indent=2)}",
                reported_lint_errs,
                entities,
            )
        return entities

    return parse_inner


@pytest.fixture
def html_loader() -> Callable[[str | Path], str]:
    """
    Fixture that returns a function to load html resources from disk

    Returns:
        Callable[[str | Path], str]: Function that loads html from disk to be
        used in tests
    """

    def load_inner(path: str | Path) -> str:
        if not isinstance(path, Path):
            path = Path(path)
        return path.read_text()

    return load_inner


@pytest.fixture
def html_table() -> Callable[[List[List[str]]], str]:
    def label_structure(content: str) -> List[str]:
        label_regex = r"^(?P<label>[\w\s\d()]+:?)(?P<brief>[\w\s\d,\".]*)$"
        match = re.search(label_regex, content)
        if match:
            return list(match.groups())
        return [content]

    def table_inner(table: List[List[str]]) -> str:
        content = ""
        for i, tr in enumerate(table):
            content += "<tr>\n"
            for j, td in enumerate(tr):
                if i == 0:
                    content += (
                        f"<th class='tcell0'><p><span class='txtfmt1'>{td}"
                        "</span></p></th>\n"
                    )
                else:
                    if j != 0:
                        content += "<td><p>\n"
                        labels = label_structure(td)
                        for k, txt in enumerate(labels):
                            if k == 0:
                                content += f"<span class='txtfmt1'>{txt}</span>\n"
                            elif txt != "":
                                content += f"<span>{txt}</span>\n"
                        content += "</p></td>\n"
                    else:
                        content += f"<td><p><span>{td}</span></p></td>\n"
            content += "</tr>\n"
        return HTML_TABLE_TEMPLATE.format(content=content, colspan=len(tr))

    return table_inner


@pytest.fixture
def html_doc() -> Callable[[str], str]:
    def doc_inner(body_content: str) -> str:
        return HTML_DOC_TEMPLATE.format(body=body_content)

    return doc_inner


HTML_TABLE_TEMPLATE = """
        <table>
        <tr>
            <td colspan="{colspan}">
                <p>
                    <span>Figure </span><span>0</span><span>: Test</span>
                </p>
            </td>
        </tr>
        {content}
        </table>

"""

HTML_DOC_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" data-spec="Spex test case" data-revision="1" />
    <title>Spex test case</title>
    <style>
        body {{
            font-family: sans-serif;
        }}

        p:first-child {{
            margin-top: .3em;
        }}

        p:last-child {{
            margin-bottom: .3em;
        }}

        p {{
            margin-top: 0em;
            margin-left: .2em;
            margin-right: .2em;
        }}

        table,
        td,
        th {{
            border-collapse: collapse;
            border: 1px solid black;
            ;
        }}

        table {{
            margin-left: .3em;
            margin-right: .3em;
            margin-bottom: 3em;
            margin-top: 1em;
        }}

        td table {{
            margin-bottom: 1em;
        }}
    </style>
</head>
<body>
{body}
</body>
</html>
"""
