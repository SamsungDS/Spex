# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause
import json
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
                f" {json.dumps(reported_lint_errs, indent=4)}"
                f" {json.dumps(entities, indent=4)}",
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
