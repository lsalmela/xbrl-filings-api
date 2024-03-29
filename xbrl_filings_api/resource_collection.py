"""Define class `ResourceCollection`."""

# SPDX-FileCopyrightText: 2023 Lauri Salmela <lauri.m.salmela@gmail.com>
#
# SPDX-License-Identifier: MIT

from collections.abc import Iterable, Iterator
from datetime import date, datetime
from typing import Any, Optional, Union

from xbrl_filings_api.api_resource import APIResource
from xbrl_filings_api.constants import DataAttributeType
from xbrl_filings_api.filing import Filing


class ResourceCollection:
    """
    Collection of subresources of a `FilingSet` object.

    The subresources are all other `APIResource` subclasses except
    `Filing` objects.

    This object is a `collections.abc.Collection` which means it may be
    iterated over, it defines `len()` as well as operator `in`. It may
    not, however, be accessed with an indexer (e.g. `object[index]`) or
    reversed.

    This collection is a view to the resources of the `FilingSet`.
    Adding or removing filings from the `filingset` attribute object
    will change the set of resources in this collection.

    Attributes
    ----------
    filingset : FilingSet
    item_class : type
    columns : list of str
    exist : bool
    """

    def __init__(
            self, filingset: Any, attr_name: str, item_class: type[APIResource]
            ) -> None:
        self.filingset = filingset
        """Reference to the FilingSet object."""

        self.item_class = item_class
        """Type object of the items within."""

        self._attr_name = attr_name
        self._columns: Union[list[str], None] = None

    def __iter__(self) -> Iterator[APIResource]:
        """Return iterator for subresources."""
        filing: Filing
        yielded_ids = set()
        for filing in self.filingset:
            attr_val = getattr(filing, self._attr_name)
            if attr_val:
                if isinstance(attr_val, set):
                    resource: APIResource
                    for resource in attr_val:
                        # Multiple filings cannot share validation
                        # messages, but here for completeness
                        if resource.api_id not in yielded_ids:
                            yielded_ids.add(resource.api_id)
                            yield resource
                elif attr_val.api_id not in yielded_ids:
                    yielded_ids.add(attr_val.api_id)
                    yield attr_val

    def __len__(self) -> int:
        """Return count of subresources."""
        count = 0
        for _ in self:
            count += 1
        return count

    def __contains__(self, item: Any) -> bool:
        """Return `True` if is instance of `item_class` and `api_id` exists."""
        if not isinstance(item, self.item_class):
            return False
        match_id = item.api_id
        for resource in self:
            if resource.api_id == match_id:
                return True
        return False

    def get_pandas_data(
            self, attr_names: Optional[Iterable[str]] = None, *,
            strip_timezone: bool = True, date_as_datetime: bool = True,
            include_urls : bool = False
            ) -> dict[str, list[DataAttributeType]]:
        """
        Get data for `pandas.DataFrame` constructor for subresources.

        A new dataframe can be instantiated for example for entities as
        follows::

        >>> import pandas as pd
        >>> df = pd.DataFrame(data=filingset.entities.get_pandas_data())

        If `attr_names` is not given, most data attributes will be
        extracted.

        Parameters
        ----------
        attr_names: iterable of str, optional
            Valid attribute names of resource object.
        strip_timezone : bool, default True
            Strip timezone information (always UTC) from `datetime`
            values.
        date_as_datetime : bool, default True
            Convert `date` values to naive `datetime` to be converted to
            `datetime64` by pandas.
        include_urls : bool, default False
            When `attr_names` is not given, include attributes ending
            ``_url``.

        Returns
        -------
        dict of str: list of DataAttributeType
            Column names are the same as the attributes for resource of
            this type.
        """
        data: dict[str, list[DataAttributeType]]
        if attr_names:
            data = {col: [] for col in attr_names}
        else:
            data = {col: [] for col in self.columns}
            if not include_urls:
                url_cols = [col for col in data if col.endswith('_url')]
                for col in url_cols:
                    del data[col]
        for resource in self:
            for col_name in data:
                val = getattr(resource, col_name)
                if strip_timezone and isinstance(val, datetime):
                    val = val.replace(tzinfo=None)
                if (date_as_datetime
                        and isinstance(val, date)
                        and type(val) is not datetime):
                    val = datetime.fromordinal(val.toordinal())
                data[col_name].append(val)
        return data

    @property
    def columns(self) -> list[str]:
        """List of available columns for resources of this type."""
        if self._columns:
            return self._columns
        self._columns = self.item_class.get_columns()
        return self._columns

    @property
    def exist(self) -> bool:
        """
        True if any resources of this type exist.

        This property is faster than ``len(obj) != 0``.
        """
        filing: Filing
        for filing in self.filingset:
            if getattr(filing, self._attr_name):
                return True
        return False

    def __repr__(self) -> str:
        """Return string repr of resource collection."""
        return (
            f'{type(self).__name__}('
            f'item_class={self.item_class!r}, '
            f'len()={len(self)})'
            )
