"""
Configure logging for Spex program.

This module configures logging for Spex using the `loguru` package.
Two loggers are installed:
1) console logger
2) file logger (to 'spex.log' in current working directory)


The console logger(1) is intended for the end-user. Messages here should be
understandable by the intended end-user. However, this log is not for debugging,
so DEBUG-level messages and stack traces are omitted.

The file logger(2) is intended for bug reports and debugging. Each line is a
separate entry formatted as a JSON object. In case `logger.exception()` is
called, then the entry contains an `exception` key containing a JSON object
representing the exception, nested exception(s) and their stack traces.
"""
import json
import os
import sys
import traceback
from pathlib import Path

from loguru import logger

# If `SPEX_DEBUG` is true then the console logger includes program-specific
# log message levels and formatted stack traces
DEBUG = os.environ.get("SPEX_DEBUG", "0").lower().strip() in {"true", "yes", "1"}


def exc_get_traceback(exc):
    if hasattr(exc, "traceback"):
        return exc.traceback
    elif hasattr(exc, "__traceback__"):
        return exc.__traceback__
    raise RuntimeError("exception has no traceback/__traceback__ attr") from exc


def jsonify_exc(exc):
    tb = exc_get_traceback(exc)
    ss = traceback.extract_tb(tb)

    exc_json = {
        "type": type(exc).__qualname__,
        "msg": str(exc),
        "frames": [
            {
                "name": frame.name,
                "file": frame.filename,
                "lineno": frame.lineno,
                "line": frame.line,
            }
            for frame in ss
        ],
    }
    if hasattr(exc, "__cause__") and exc.__cause__:
        print("CAUSE")
        print(repr(exc.__cause__))
        print("/CAUSE")
        exc_json["cause"] = jsonify_exc(exc.__cause__)

    return exc_json


SPEX_LOG_PATH = Path.cwd() / "spex.log"
SPEX_LOG_PATH.unlink(missing_ok=True)


def fmt_no_stacktrace(rec):
    if rec["level"].name == "U_CRITICAL":
        return "<level>•</level> <bg red><white>{message}</white></bg red>\n"
    return "<level>•</level> {message}\n"


logger.remove()  # remove all loggers


# define specific log levels for user-oriented logging messages
class ULog:
    """Log-levels for logging messages intended for the end-user

    Levels loosely follow standard log level definitions
    (https://loguru.readthedocs.io/en/stable/api/logger.html#levels)

    With a severity offset of 50 to put all levels above the standard logging
    levels.
    This permits us to filter lower (or all) regular log levels while still
    having several user-specific log levels with which to differentiate messages.
    """

    INFO = "U_INFO"
    SUCCESS = "U_SUCCESS"
    WARNING = "U_WARNING"
    ERROR = "U_ERROR"
    LINT = "U_LINT"
    CRITICAL = "U_CRITICAL"

    # ... poor man's public final
    def __setattr__(self, key, value):
        raise AttributeError("cannot modify values in this class")

    def __delattr__(self, item):
        raise AttributeError("cannot modify values in this class")


logger.level(ULog.INFO, no=70)
logger.level(ULog.SUCCESS, no=75, color="<green>")
logger.level(ULog.WARNING, no=80, color="<yellow>")
logger.level(ULog.ERROR, no=90, color="<red>")
logger.level(ULog.LINT, no=95, color="<blue>")
logger.level(ULog.CRITICAL, no=100, color="<red>")


# add console logger, don't log stack traces (they flood output)
logger.add(
    sys.stderr,
    colorize=True,
    backtrace=True if DEBUG else False,
    diagnose=True if DEBUG else False,
    format=("<level>{level}</level> {message}" if DEBUG else fmt_no_stacktrace),
    level="DEBUG" if DEBUG else ULog.INFO,
)


class LogFileSerializer:
    def __init__(self, fpath: Path):
        self._fpath = fpath
        self._fp = open(fpath, "w")

    def __call__(self, message):
        record = message.record
        log = {
            "level": record["level"].name,
            "msg": record["message"],
            "file": record["file"].path,
            "func": record["function"],
            "line": record["line"],
        }
        if record["extra"]:
            log["extra"] = record["extra"]
        if record["exception"]:
            exc = record["exception"].value
            log["exception"] = jsonify_exc(exc)
        # self._fp.write(json.dumps(log))
        print(json.dumps(log), file=self._fp)

    def __del__(self):
        self._fp.close()


logger.add(
    LogFileSerializer(SPEX_LOG_PATH),
    serialize=True,
    backtrace=True,
    diagnose=True,
    level="DEBUG",
)
