# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause


from typing import Any, Optional


class XPathException(Exception):
    message: str
    query: Optional[str]
    details: Optional[Any]

    def __init__(
        self, message: str, query: Optional[str], details: Optional[Any] = None
    ) -> None:
        super().__init__(message)

        self.message: str = message
        self.query: Optional[str] = query
        self.details: Optional[Any] = details


class XPathElementNotFoundException(XPathException):
    message: str
    query: Optional[str]
    details: Optional[Any]

    def __init__(
        self, message: str, query: Optional[str], details: Optional[Any] = None
    ) -> None:
        super().__init__(message, details)

        self.message: str = message
        self.query: Optional[str] = query
        self.details: Optional[Any] = details


class XPathInvalidQueryException(XPathException):
    message: str
    query: Optional[str]
    details: Optional[Any]

    def __init__(
        self, message: str, query: Optional[str], details: Optional[Any] = None
    ) -> None:
        super().__init__(message, details)

        self.message: str = message
        self.query: Optional[str] = query
        self.details: Optional[Any] = details


class LabelExtractionError(Exception):
    """Custom exception raised for errors in label extraction."""

    def __init__(self, message="Error occurred while extracting label"):
        self.message = message
        super().__init__(self.message)
