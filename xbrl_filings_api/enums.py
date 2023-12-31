"""Enums for the package."""

# SPDX-FileCopyrightText: 2023 Lauri Salmela <lauri.m.salmela@gmail.com>
#
# SPDX-License-Identifier: MIT

from enum import Enum, Flag, auto


class _ParseType(Enum):
    """Instuctions how to parse JSON key paths in API responses."""

    DATE = auto()
    """Parsed into `datetime.date`."""

    DATETIME = auto()
    """
    Parsed into timezone-aware `datetime.datetime`.

    Timezone will be the one specified in the string or UTC, if
    unspecified.
    """

    URL = auto()
    """Relative URLs will be parsed into absolute URLs."""


class ScopeFlag(Flag):
    """Flags for API resource retrieval scope."""

    GET_ONLY_FILINGS = auto()
    """Retrieve only filings and nothing else. Overrides other flags."""

    GET_ENTITY = auto()
    """Retrieve entities of filings."""

    GET_VALIDATION_MESSAGES = auto()
    """Retrieve validation messages of filings."""


GET_ONLY_FILINGS = ScopeFlag.GET_ONLY_FILINGS
GET_ENTITY = ScopeFlag.GET_ENTITY
GET_VALIDATION_MESSAGES = ScopeFlag.GET_VALIDATION_MESSAGES
