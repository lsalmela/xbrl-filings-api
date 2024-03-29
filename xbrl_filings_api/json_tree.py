"""Define `_JSONTree` class and related dataclasses."""

# SPDX-FileCopyrightText: 2023 Lauri Salmela <lauri.m.salmela@gmail.com>
#
# SPDX-License-Identifier: MIT

import logging
import urllib.parse
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, ClassVar, Optional, Union

from xbrl_filings_api import options
from xbrl_filings_api.enums import _ParseType

UTC = timezone.utc
logger = logging.getLogger(__name__)


@dataclass
class _RetrieveCounter:
    success_count: int
    total_count: int


@dataclass(order=True, frozen=True)
class KeyPathRetrieveCounts:
    """Stores retrieve counts for JSON key paths of `class_name`."""

    class_name: str
    """Name of the `APIObject` class."""
    key_path: str
    """Key access path in the JSON fragment of the API object."""
    success_count: int
    """Number of successful reads with a value other than `None`."""
    total_count: int
    """Number of total reads."""


class _JSONTree:
    """
    Object for traversing and parsing API response.

    When the required keys have been read, `close` method must be called
    in the init methods of `APIObject` subclasses. This ensures the keys
    which were never accessed (novel API features) are available via the
    two class methods.

    The class methods `get_unaccessed_key_paths` and
    `get_key_path_availability_counts` are preferred to be called via
    the identically named functions of the `debug` module.

    Attributes
    ----------
    class_name : str
    tree : dict or None
    do_not_track : bool

    Class attributes
    ----------------
    unexpected_resource_types: set of tuples (str, str)
    """

    _unaccessed_paths: ClassVar[dict[str, set[str]]] = {}
    """
    Unaccessed key paths of API objects.

    Content::

        _unaccessed_paths[class_name] = {key_path1, key_path2, ...}
    """

    _object_path_counter: ClassVar[dict[str, dict[str, _RetrieveCounter]]] = {}
    """
    Counter of key path access of API objects.

    Content::

        _object_path_counter[class_name][key_path] = _RetrieveCounter()
    """

    unexpected_resource_types: ClassVar[set[tuple[str, str]]] = set()
    """
    Set of unexpected API resource types.

    Read by calling function `debug.get_unexpected_resource_types`.

    Content::

        unexpected_resource_types.pop() = (type_str, origin)
    """

    def __init__(
            self,
            *,
            class_name: str,
            json_frag: Union[dict, None],
            do_not_track: bool = False
            ) -> None:
        """
        Initialize a _JSONTree instance.

        Parameters
        ----------
        class_name : str
            The `__qualname__` of the parent `APIObject` subclass.
        json_frag : dict or None
            The underlying JSON:API unserialized JSON as a dictionary
            structure. An `_APIPage` contains the whole document.
        do_not_track : bool, default False
            When `True`, does not track successful and total `get`
            method calls, available via function
            `debug.get_key_path_availability_counts`.
        """
        self.class_name = class_name
        """
        `__qualname__` of the `APIObject` subclass this tree is read
        for.
        """
        self.tree: Union[dict[str, Any], None] = json_frag
        """
        JSON:API fragment as Python dict from argument `json_frag` for
        querying.
        """
        self.do_not_track = do_not_track
        """
        When `True`, does not track successful and total `get` method
        calls.
        """

        opcounter = self._object_path_counter
        if not opcounter.get(self.class_name):
            opcounter[self.class_name] = {}
        upaths = self._unaccessed_paths
        if not upaths.get(self.class_name):
            upaths[self.class_name] = set()

    def get(
            self, key_path: str, parse_type: Optional[_ParseType] = None
            ) -> Any:
        """
        Read JSON data from dict and parse values to Python literals.

        Value `_ParseType.DATETIME` of `parse_type` parses ISO style UTC
        strings such as '2023-05-09 10:51:50.382633'. The return value
        is locale-aware and if the string does not specify timezone, it
        will be on UTC.

        Value `_ParseType.DATE` parses naive dates and `_ParseType.URL`
        resolves relative URLs based on `options.entry_point_url`.

        Parameters
        ----------
        key_path : str
            A dot-delimited key path for navigation in a deeply nested
            serialized JSON object.
            E.g. 'relationships.validation_messages.links.related'.
        parse_type : _ParseType member, optional
            One of the `_ParseType` Enum members.
        """
        if self.tree is None:
            msg = 'Cannot call get() when _JSONTree has been closed'
            raise Exception(msg)
        key_value = None
        comps = key_path.split('.')
        subdict: dict[str, Any] = self.tree
        last_i = len(comps) - 1
        for comp_i, comp in enumerate(comps):
            key_value = subdict.get(comp)
            if key_value is None:
                break
            elif isinstance(key_value, dict):
                if comp_i < last_i:
                    subdict = key_value
                else:
                    # Value of key_path is a dict
                    break
            else:
                # Get actual existing non-dict value of key_path
                if isinstance(key_value, str):
                    key_value = self._parse_value(
                        key_value, parse_type, key_path)
                break

        if self.do_not_track is False:
            opcounter = self._object_path_counter
            if not opcounter[self.class_name].get(key_path):
                init_count = 0 if key_value is None else 1
                opcounter[self.class_name][key_path] = (
                    _RetrieveCounter(success_count=init_count, total_count=1))
            else:
                counter = opcounter[self.class_name][key_path]
                if key_value is not None:
                    counter.success_count += 1
                counter.total_count += 1
        return key_value

    def close(self) -> None:
        """
        Close JSON tree for reading.

        Remember all unaccessed and never existing key paths in the
        nested dictionary structure but skip lists.
        """
        if self.do_not_track:
            return
        if self.tree is None:
            msg = 'Cannot close the same object more than once'
            raise Exception(msg)
        for key in self.tree:
            self._find_unaccessed(self.tree, [key])
        self.tree = None

    def _find_unaccessed(
            self, json_frag: dict, comps: list[str]) -> None:
        """
        Traverse the whole JSON tree/fragment by recursion.

        List values are skipped.
        """
        opcounter = self._object_path_counter
        last_comp = comps[len(comps) - 1]
        key_value = json_frag.get(last_comp)
        if isinstance(key_value, dict):
            for key in key_value:
                comps_copy = comps.copy()
                comps_copy.append(key)
                self._find_unaccessed(key_value, comps_copy)
        elif '.'.join(comps) not in opcounter[self.class_name]:
            self._unaccessed_paths[self.class_name].add('.'.join(comps))

    def _parse_value(
            self, key_value: str, parse_type: Union[_ParseType, None],
            key_path: str
            ) -> Union[datetime, date, str, None]:
        """Parse string value of `key_path` based on `parse_type`."""
        if parse_type == _ParseType.DATETIME:
            parsed_dt = None
            for try_i in range(2):
                try:
                    if try_i == 0:
                        parsed_dt = datetime.fromisoformat(key_value)
                    else:
                        # For Python 3.10 and earlier in case timezones
                        # are taken to use in API datetime strings
                        parsed_dt = datetime.strptime(
                            key_value, '%Y-%m-%d %H:%M:%S.%f%z')
                except ValueError:
                    pass
            if parsed_dt is None:
                msg = (
                    f'Could not parse ISO datetime string {key_value!r} for '
                    f'{self.class_name} object JSON fragment path '
                    f'{key_path!r}.'
                    )
                logger.warning(msg, stacklevel=2)
            if parsed_dt is None:
                return None
            isnaive = not isinstance(parsed_dt.tzinfo, timezone)
            if isnaive:
                parsed_dt = parsed_dt.replace(tzinfo=UTC)

            return parsed_dt

        elif parse_type == _ParseType.DATE:
            parsed_date = None
            try:
                parts = [int(part) for part in key_value.split('-')]
                parsed_date = date(*parts)
            except ValueError:
                msg = (
                    f'Could not parse ISO date string {key_value!r} for '
                    f'{self.class_name} object JSON fragment path '
                    f'{key_path!r}.'
                    )
                logger.warning(msg, stacklevel=2)
            return parsed_date

        elif parse_type == _ParseType.URL:
            parsed_url = None
            try:
                parsed_url = urllib.parse.urljoin(
                    options.entry_point_url, key_value)
            except ValueError:
                msg = (
                    f'Could not determine absolute URL string from '
                    f'{key_value!r} for {self.class_name} object JSON '
                    f'fragment path {key_path!r}.'
                    )
                logger.warning(msg, stacklevel=2)
            return parsed_url

        return key_value

    @classmethod
    def get_unaccessed_key_paths(cls) -> set[tuple[str, str]]:
        """
        Get unaccessed JSON key paths of objects.

        Get the set of unaccessed key paths in unserialized JSON
        fragments of API responses. List values (JSON arrays) are listed
        as a single path.
        """
        unaccessed: set[tuple[str, str]] = set()
        for class_name, key_path_set in cls._unaccessed_paths.items():
            unaccessed.update(
                (class_name, key_path) for key_path in key_path_set)
        return unaccessed

    @classmethod
    def get_key_path_availability_counts(cls) -> set[KeyPathRetrieveCounts]:
        """
        Get counts of key paths that did not resolve to `None`.

        Get the set of successful retrieval counts for key paths in
        unserialized JSON fragments of API responses.
        """
        availability: set[KeyPathRetrieveCounts] = set()
        for class_name, key_path_dict in cls._object_path_counter.items():
            availability.update((
                KeyPathRetrieveCounts(
                    class_name, key_path, counter.success_count,
                    counter.total_count
                    )
                for key_path, counter in key_path_dict.items()
                ))
        return availability
