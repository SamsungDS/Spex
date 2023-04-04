from typing import Any, Union, List
from loguru import logger
from spex.logging._log_config import ULog

def __do_log(level: str, message: Union[str, List[str]], *args: Any, **kwargs: Any):
    if isinstance(message, list):
        # NOTE: this relies on the log prefix always being a single character
        message = "\n  ".join(message)
    logger.log(level, message, *args, **kwargs)


def info(message: Union[str, List[str]], *args: Any, **kwargs: Any) -> None:
    __do_log(ULog.INFO, message, *args, **kwargs)


def success(message: Union[str, List[str]], *args: Any, **kwargs: Any) -> None:
    __do_log(ULog.SUCCESS, message, *args, **kwargs)


def warning(message: Union[str, List[str]], *args: Any, **kwargs: Any) -> None:
    __do_log(ULog.WARNING, message, *args, **kwargs)


def error(message: Union[str, List[str]], *args: Any, **kwargs: Any) -> None:
    __do_log(ULog.ERROR, message, *args, **kwargs)


def lint(message: Union[str, List[str]], *args: Any, **kwargs: Any) -> None:
    __do_log(ULog.LINT, message, *args, **kwargs)


def critical(message: Union[str, List[str]], *args: Any, **kwargs: Any) -> None:
    __do_log(ULog.CRITICAL, message, *args, **kwargs)
