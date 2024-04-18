# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause
from pathlib import Path
from typing import List, Optional

from spex.jsonspec.lint import Code


class ParserArgs:
    # NOTE: Validation here is rudimentary. Pure Python validation is tedious
    #       if you wish to aggregate all input errors and to retain information
    #       on the source of errors (which list items, which attributes).
    #
    #       Thus this just raises an error on first invalid input. We expect
    #       this layer to catch programming errors (missing validation) in
    #       higher layers.
    output_dir: Optional[Path]
    skip_fig_on_error: bool
    lint_codes_ignore: List[Code]
    validate_json: bool

    def __init__(
        self,
        *,
        output_dir: Path,
        lint_codes_ignore: Optional[List[Code]] = None,
        skip_fig_on_error: bool = False,
        validate_json: bool = False,
    ):
        if not isinstance(output_dir, Path):
            raise ValueError("output_dir is not a Path instance")
        elif not output_dir.is_dir():
            raise ValueError("output_dir is not a directory")

        if lint_codes_ignore:
            for lint_code in lint_codes_ignore:
                if not isinstance(lint_code, Code):
                    raise ValueError("not a linting code")

        if not isinstance(skip_fig_on_error, bool):
            raise ValueError("skip_fig_on_err must be a boolean")

        self.output_dir = output_dir
        self.lint_codes_ignore = lint_codes_ignore or []
        self.skip_fig_on_error = skip_fig_on_error
        self.validate_json = validate_json
