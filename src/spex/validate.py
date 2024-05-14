# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

import json
from importlib import resources
from pathlib import Path

from jsonschema import validate


def validate_json(document_path: Path) -> None:
    schema = (
        resources.files("spex.resources").joinpath("stage2.schema.json").read_text()
    )
    document = document_path.read_text()
    validate(json.loads(document), json.loads(schema))
