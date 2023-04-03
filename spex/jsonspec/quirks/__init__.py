from typing import TYPE_CHECKING, Dict, Tuple, Type
from spex.jsonspec.quirks.zoned import NvmCsZoned11c
from spex.jsonspec.quirks.nvm import NvmCmdSet1c


if TYPE_CHECKING:
    from spex.jsonspec.document import DocumentParser


QuirksMap = Dict[Tuple[str, str], Type["DocumentParser"]]

QUIRKS_MAP: QuirksMap = {
    ("nvm express® nvm command set specification", "1.0c"): NvmCmdSet1c,
    ("nvm express® zoned namespace command set specification", "1.1c"): NvmCsZoned11c,
}
