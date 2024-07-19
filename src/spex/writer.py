# SPDX-FileCopyrightText: 2024 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause

import json
from io import TextIOWrapper
from pathlib import Path
from types import TracebackType
from typing import Dict, List, Optional, Protocol, TypedDict

from spex.jsonspec.defs import JSON


class S2Model(TypedDict):
    meta: Dict[str, JSON]
    entities: List[JSON]


class Writer(Protocol):
    def __enter__(self) -> "Writer":
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        ...

    def write_meta(self, key: str, val: JSON) -> None:
        ...

    def write_entity(self, entity: JSON) -> None:
        ...

    @property
    def path(self) -> Optional[Path]:
        ...


class StdoutWriter(Writer):
    def __init__(self, src: Path):
        self._src = src
        self._doc: S2Model = {
            "meta": {},
            "entities": [],
        }

    def write_meta(self, key: str, val: JSON) -> None:
        self._doc["meta"][key] = val

    def write_entity(self, entity: JSON) -> None:
        self._doc["entities"].append(entity)

    def __enter__(self) -> "Writer":
        return self

    @property
    def path(self) -> Optional[Path]:
        return None

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        # retain UTF-8 characters in output
        # res = json.dumps(self._doc, indent=2, ensure_ascii=False).encode("utf-8")
        # print(res.decode())
        if exc_val is not None:
            raise exc_val


class FileWriter:
    def __init__(self, output: Path, src: Path):
        fname = src.name[: -len(src.suffix)]
        self._output = output / f"{fname}.json"
        self._src = src
        self._dst: Optional[TextIOWrapper] = open(self._output, "w")
        self._doc: S2Model = {
            "meta": {},
            "entities": [],
        }

    def write_meta(self, key: str, val: JSON) -> None:
        self._doc["meta"][key] = val

    def write_entity(self, entity: JSON) -> None:
        self._doc["entities"].append(entity)

    @property
    def path(self) -> Optional[Path]:
        return self._output

    def __enter__(self) -> "Writer":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._dst is not None:
            try:
                json.dump(self._doc, self._dst, indent=2, ensure_ascii=False)
            finally:
                self._dst.close()
        self._dst = None
        if exc_val is not None:
            raise exc_val
