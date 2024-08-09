# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path
from subprocess import run


def test_end2end(tmp_path: Path):
    cmd = [
        f"spex --skip-figure-on-error --output {str(tmp_path)} example/stage1/*.html",
    ]
    result = run(cmd, capture_output=True, shell=True)
    assert result.returncode == 0
