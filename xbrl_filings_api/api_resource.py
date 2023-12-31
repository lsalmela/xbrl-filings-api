"""Define `APIResource` class."""

# SPDX-FileCopyrightText: 2023 Lauri Salmela <lauri.m.salmela@gmail.com>
#
# SPDX-License-Identifier: MIT

from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any, Optional, Union

from xbrl_filings_api import order_columns
from xbrl_filings_api.api_object import APIObject
from xbrl_filings_api.api_request import _APIRequest
from xbrl_filings_api.constants import ATTRS_ALWAYS_EXCLUDE_FROM_DATA
from xbrl_filings_api.enums import GET_ENTITY, GET_ONLY_FILINGS, ScopeFlag

EllipsisType = type(Ellipsis) # No valid solution for Python 3.9
UTC = timezone.utc


class APIResource(APIObject):
    """
    A JSON:API resource.

    Subclasses of this class may be read into a database. An instance
    resembles a database record.

    Attributes
    ----------
    api_id : str or None
    query_time : datetime
    request_url : str
    """

    TYPE: Union[str, None] = None
    _FILING_FLAG: ScopeFlag

    def __init__(
            self,
            json_frag: Union[dict[str, Any], EllipsisType],
            api_request: Union[_APIRequest, None] = None
            ) -> None:
        """
        Initialize an API resource.

        Parameters
        ----------
        json_frag : dict or ellipsis
            JSON fragment in an API response. An ellipsis (...) may be
            given to create a prototype.
        """
        is_prototype = False
        if json_frag == Ellipsis:
            is_prototype = True
            json_frag = {}
            api_request = _APIRequest('', datetime.now(UTC))
        if api_request is None:
            msg = 'Parameter api_request not given'
            raise ValueError(msg)

        super().__init__(
            json_frag=json_frag,
            api_request=api_request,
            do_not_track=is_prototype
            )

        self.api_id: Union[str, None] = None
        api_id = self._json.get('id')
        if isinstance(api_id, str):
            self.api_id = api_id
        """``id`` from JSON:API."""

    @classmethod
    def get_data_attributes(
            cls, flags: Optional[ScopeFlag] = None,
            filings: Optional[Iterable['APIResource']] = None
            ) -> list[str]:
        """
        Get data attributes for an API resource subclass.

        Excludes internal and class attributes and the ones containing
        objects.

        For `Filing` objects this also means excluding attributes ending
        ``_download_path`` if all filings have this column filled with
        `None`. Additionally, if `GET_ENTITY` is not set filings will
        exclude `entity_api_id`.

        Parameters
        ----------
        flags : ScopeFlag, optional
            Only relevant for `Filing` resource type.
        filings : iterable of Filing, optional
            Only relevant for `Filing` resource type.
        """
        if cls is APIResource:
            raise NotImplementedError()
        resource_proto = cls(...)
        attrs = [
            attr for attr in dir(resource_proto)
            if not (
                attr.startswith('_')
                or attr.endswith('_time_str')
                or getattr(cls, attr, False)
                or attr in ATTRS_ALWAYS_EXCLUDE_FROM_DATA)
            ]
        if cls.TYPE == 'filing':
            if filings:
                exclude_dlpaths = (
                    cls._get_unused_download_paths(filings))
                attrs = [attr for attr in attrs if attr not in exclude_dlpaths]
            if flags and GET_ENTITY not in flags:
                attrs.remove('entity_api_id')
        return order_columns.order_columns(attrs)

    @classmethod
    def _get_unused_download_paths(cls, filings: Iterable[Any]) -> set[str]:
        """
        Get unused `Filing` object download path attributes.

        Looks for attributes ending in ``_download_path``.

        Parameters
        ----------
        filings : iterable of Filing
        """
        fproto = cls(...)
        dlattrs = [
            att for att in dir(fproto)
            if not att.startswith('_') and att.endswith('_download_path')
            ]

        unused = set()
        for att in dlattrs:
            for fil in filings:
                if getattr(fil, att) is not None:
                    break
            else:
                unused.add(att)
        return unused

    @classmethod
    def get_columns(
            cls, *, filings: Union[Iterable[Any], None] = None,
            has_entities: bool = False
            ) -> list[str]:
        """
        List of available columns for this `APIResource` subclass.

        Parameters
        ----------
        filings: iterable of Filing, optional
            Only relevant for `Filing` objects.
        has_entities : bool, default False
            Only relevant for `Filing` objects.
        """
        if cls is APIResource:
            raise NotImplementedError()
        flags = GET_ONLY_FILINGS
        if has_entities:
            flags = GET_ENTITY
        cols = cls.get_data_attributes(flags, filings)
        return order_columns.order_columns(cols)
