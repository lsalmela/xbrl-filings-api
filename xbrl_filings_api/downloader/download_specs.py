"""Define class `DownloadSpecs`."""

# SPDX-FileCopyrightText: 2023 Lauri Salmela <lauri.m.salmela@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from pathlib import PurePath
from typing import Any, Optional, Union


@dataclass(frozen=True)
class DownloadSpecs:
    """
    Download specs to be consumed by `download_processor` module.

    Used as input instructions in lists for parallel download functions.
    """

    url: str
    """URL to download."""

    to_dir: Union[str, PurePath]
    """Directory to save the downloaded file."""

    stem_pattern: Optional[str] = None
    """
    Pattern to add to the filename stems.

    Placeholder ``/name/`` is always required.
    """

    filename: Optional[str] = None
    """Name to be used for the saved file."""

    sha256: Optional[str] = None
    """
    Expected SHA-256 hash as a hex string.

    Case-insensitive. No hash is calculated if this parameter is not
    given.
    """

    info: Any = None
    """Download-specific information."""
