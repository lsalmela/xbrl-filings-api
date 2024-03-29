"""
Define `FilingSet` class.

This is an extended set type with certain added attributes.

"""

# SPDX-FileCopyrightText: 2023 Lauri Salmela <lauri.m.salmela@gmail.com>
#
# SPDX-License-Identifier: MIT

from collections.abc import AsyncIterator, Collection, Iterable, Mapping
from datetime import date, datetime
from pathlib import Path, PurePath
from typing import Any, Optional, Union

import xbrl_filings_api.options as options
from xbrl_filings_api import (
    database_processor,
    download_specs_construct,
    downloader,
)
from xbrl_filings_api.api_resource import APIResource
from xbrl_filings_api.constants import DataAttributeType, FileStringType
from xbrl_filings_api.download_info import DownloadInfo
from xbrl_filings_api.download_item import DownloadItem
from xbrl_filings_api.entity import Entity
from xbrl_filings_api.enums import (
    GET_ENTITY,
    GET_ONLY_FILINGS,
    GET_VALIDATION_MESSAGES,
    ScopeFlag,
)
from xbrl_filings_api.exceptions import CorruptDownloadError
from xbrl_filings_api.filing import Filing
from xbrl_filings_api.resource_collection import ResourceCollection
from xbrl_filings_api.validation_message import ValidationMessage


class FilingSet(set[Filing]):
    """Set for `Filing` objects.

    The class is an extended set type with certain filing-related
    attributes and functionality.

    Attributes
    ----------
    entities : ResourceCollection
    validation_messages : ResourceCollection
    columns : list of str
    """

    def __init__(self, filings: Optional[Iterable[Filing]] = None) -> None:
        if filings is None:
            super().__init__()
        else:
            super().__init__(filings)
        self.entities = ResourceCollection(self, 'entity', Entity)
        self.validation_messages = ResourceCollection(
            self, 'validation_messages', ValidationMessage)

    def download(
            self,
            files: Union[
                FileStringType,
                Iterable[FileStringType],
                Mapping[FileStringType, DownloadItem]
                ],
            to_dir: Union[str, PurePath, None] = None,
            *,
            stem_pattern: Union[str, None] = None,
            check_corruption: bool = True,
            max_concurrent: Union[int, None] = 5,
            ) -> None:
        """
        Download files according to `files` parameter.

        The filesystem path of the downloaded file will be saved in the
        `Filing` object attributes {file}_download_path such as
        ``json_download_path`` for the downloaded JSON file.

        If there are ``package`` download definition(s) in the parameter
        `files` and parameter `check_corruption` is True, the downloaded
        package files will be checked through the `package_sha256`
        attribute of `Filing` objects. If this hash attribute does not
        match the one calculated from the downloaded file, an exception
        `CorruptDownloadError` of the first erraneous occurrence will be
        raised after all downloads have finished. The downloaded file(s)
        will not be deleted but the filename(s) will be appended with
        ending ``.corrupt``. However, attributes {file}_download_path
        will not store these corrupt paths.

        The directories in `to_dir` will be created if they do not
        exist. By default, filename is derived from download URL. If the
        file already exists, it will be overwritten.

        If download is interrupted, the files will be left with ending
        ``.unfinished``.

        If no name could be derived from `url`, the file will be named
        ``file0001``, ``file0002``, etc. In this case a new file is
        always created.

        Parameter `stem_pattern` requires a placeholder ``/name/``. For
        example pattern ``/name/_second_try`` will change original
        filename ``743700XJC24THUPK0S03-2022-12-31-fi.xhtml`` into
        ``743700XJC24THUPK0S03-2022-12-31-fi_second_try.xhtml``. Not
        recommended for packages as their names should not be changed.

        HTTP request timeout is defined in `options.timeout_sec`.

        Parameters
        ----------
        files : str or iterable of str or mapping of str: DownloadItem
            Value, iterable item or mapping key must be in
            ``{'json', 'package', 'xhtml'}``. `DownloadItem` attributes
            override method parameters for a single file.
        to_dir : str or pathlike, optional
            Directory to save the files. Defaults to working directory.
        stem_pattern : str, optional
            Pattern to add to the filename stems. Placeholder ``/name/``
            is always required.
        check_corruption : bool, default True
            Calculate hashes for package files.
        max_concurrent : int or None, default None
            Maximum number of simultaneous downloads allowed. Value
            `None` means unlimited.

        Raises
        ------
        CorruptDownloadError
            Filing attribute `package_sha256` does not match the
            calculated hash of package file.
        requests.HTTPError
            HTTP status error occurs.
        requests.ConnectionError
            Connection fails.
        """
        downloader.validate_stem_pattern(stem_pattern)

        items = []
        for filing in self:
            items.extend(
                download_specs_construct.construct(
                    files, filing, to_dir, stem_pattern,
                    Filing.VALID_DOWNLOAD_FORMATS,
                    check_corruption=check_corruption,
                    isfilingset=True
                    ))
        results = downloader.download_parallel(
            items,
            max_concurrent=max_concurrent,
            timeout=options.timeout_sec
            )
        for result in results:
            if result.path:
                res_info: DownloadInfo = result.info
                setattr(
                    res_info.obj,
                    f'{res_info.file}_download_path',
                    result.path
                    )
        excs = [
            result.err for result in results
            if isinstance(result.err, Exception)
            ]
        for err_i, err in enumerate(excs):
            if isinstance(err, downloader.CorruptDownloadError):
                # Wrap again with FilingsAPIError subclassed exception
                excs[err_i] = CorruptDownloadError(
                    path=err.path,
                    url=err.url,
                    calculated_hash=err.calculated_hash,
                    expected_hash=err.expected_hash
                    )
        if excs:
            raise excs[0]

    async def download_aiter(
            self,
            files: Union[
                FileStringType,
                Iterable[FileStringType],
                Mapping[FileStringType, DownloadItem]
                ],
            to_dir: Union[str, PurePath, None] = None,
            *,
            stem_pattern: Union[str, None] = None,
            check_corruption: bool = True,
            max_concurrent: Union[int, None] = 5
            ) -> AsyncIterator[downloader.DownloadResult]:
        """
        Download files in type or types of `files`.

        The function follows the same logic as method `download()`. See
        documentation.

        Parameters
        ----------
        files : str or iterable of str or mapping of str: DownloadItem
            Value, iterable item or mapping key must be in
            ``{'json', 'package', 'xhtml'}``. `DownloadItem` attributes
            override method parameters for a single file.
        to_dir : str or pathlike, optional
            Directory to save the files. Defaults to working directory.
        stem_pattern : str, optional
            Pattern to add to the filename stems. Placeholder ``/name/``
            is always required.
        check_corruption : bool, default True
            Calculate hashes for package files.
        max_concurrent : int or None, default 5
            Maximum number of simultaneous downloads allowed. Value
            `None` means unlimited.

        Yields
        ------
        DownloadResult
            Contains information on the finished download.
        """
        downloader.validate_stem_pattern(stem_pattern)

        items = []
        for filing in self:
            items.extend(
                download_specs_construct.construct(
                    files, filing, to_dir, stem_pattern,
                    Filing.VALID_DOWNLOAD_FORMATS,
                    check_corruption=check_corruption,
                    isfilingset=True
                    ))
        dliter = downloader.download_parallel_aiter(
            items,
            max_concurrent=max_concurrent,
            timeout=options.timeout_sec
            )
        async for result in dliter:
            if result.path:
                res_info: DownloadInfo = result.info
                setattr(
                    res_info.obj,
                    f'{res_info.file}_download_path',
                    result.path
                    )
            if isinstance(result.err, downloader.CorruptDownloadError):
                # Wrap again with FilingsAPIError subclassed exception
                err = CorruptDownloadError(
                    path=result.err.path,
                    url=result.err.url,
                    calculated_hash=result.err.calculated_hash,
                    expected_hash=result.err.expected_hash
                    )
                result = downloader.DownloadResult(
                    result.url, result.path, err, result.info)
            yield result

    def to_sqlite(
            self,
            path: Union[str, Path],
            *,
            update: bool = False,
            flags: ScopeFlag = GET_ENTITY | GET_VALIDATION_MESSAGES
            ) -> None:
        """
        Save set to an SQLite3 database.

        The method has the same signature and follows the same rules as
        `to_sqlite()` with the exception of missing parameters
        `filters`, `sort`, `max_size` and `add_api_params`. See
        documentation.

        Flags also default to all tables turned on. If no additional
        information is present in the set, the tables will not be
        created if they do not exist.

        Parameters
        ----------
        path or Path
            Path to the SQLite database.
        update : bool, default False
            If the database already exists, update it with these
            records. Old records are updated and new ones are added.
        flags : ScopeFlag, default GET_ENTITY | GET_VALIDATION_MESSAGES
            Scope of saving. Flag `GET_ENTITY` will save entity records
            of filings and `GET_VALIDATION_MESSAGES` the validation
            messages.

        Raises
        ------
        FileExistsError
            When ``update=False``, if the intended save path for the
            database is an existing file.
        DatabaseSchemaUnmatchError
            When ``update=True``, if the file contains a database whose
            schema does not match the expected format.
        sqlite3.DatabaseError
            When ``update=True``, if the file is not a database
            (``err.sqlite_errorname='SQLITE_NOTADB'``) etc.
        """
        ppath = path if isinstance(path, Path) else Path(path)

        data_objs, flags = self._get_data_sets(flags)

        database_processor.sets_to_sqlite(
            flags, ppath, data_objs, update=update)

    def get_pandas_data(
            self, attr_names: Optional[Iterable[str]] = None, *,
            with_entity: bool = False, strip_timezone: bool = True,
            date_as_datetime: bool = True, include_urls : bool = False,
            include_paths : bool = False
            ) -> dict[str, list[DataAttributeType]]:
        """
        Get data as dict for `pandas.DataFrame` constructor for filings.

        A new dataframe can be instantiated by::

        >>> import pandas as pd
        >>> df = pd.DataFrame(data=filingset.get_pandas_data())

        If `attr_names` is not given, data attributes excluding ones
        ending ``_date_str`` will be extracted. Attributes ending in
        ``_download_path`` will be extracted only if at least one file
        of this type has been downloaded (and include_paths=True) and
        `entity_api_id` if there is at least one entity object in the
        set and `with_entity` is `False`.

        Parameters
        ----------
        attr_names : iterable of str, optional
            Valid attributes names of `Filing` object or ``entity.``
            prefixed attributes of its `Entity` object.
        with_entity : bool, default False
            When `attr_names` is not given, include entity attributes to
            the filing.
        strip_timezone : bool, default True
            Strip timezone information (always UTC) from `datetime`
            values.
        date_as_datetime : bool, default True
            Convert `date` values to naive `datetime` to be converted to
            `datetime64` by pandas.
        include_urls : bool, default False
            When `attr_names` is not given, include attributes ending
            ``_url``.
        include_paths : bool, default False
            When `attr_names` is not given, include attributes ending
            ``_path``.

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
            if with_entity:
                if 'entity_api_id' in data:
                    del data['entity_api_id']
                ent_cols: dict[str, list[DataAttributeType]] = {
                    f'entity.{col}': [] for col in self.entities.columns}
                data.update(ent_cols)
            if not include_urls:
                url_cols = [col for col in data if col.endswith('_url')]
                for col in url_cols:
                    del data[col]
            if not include_paths:
                path_cols = [col for col in data if col.endswith('_path')]
                for col in path_cols:
                    del data[col]
        for filing in self:
            for col_name in data:
                val: DataAttributeType = None
                if col_name.startswith('entity.'):
                    if filing.entity:
                        val = getattr(filing.entity, col_name[7:])
                else:
                    val = getattr(filing, col_name)
                if strip_timezone and isinstance(val, datetime):
                    val = val.replace(tzinfo=None)
                if (date_as_datetime
                        and isinstance(val, date)
                        and type(val) is not datetime):
                    val = datetime.fromordinal(val.toordinal())
                data[col_name].append(val)
        return data

    def pop_duplicates(
            self, languages: Union[Iterable[str], None] = ['en'], *,
            use_reporting_date: bool = False, all_markets: bool = False
            ) -> 'FilingSet':
        """
        Pops duplicates of the same enclosure from the set of filings.

        Entities must be available on the `FilingSet`.

        The method searches the `FilingSet` and leaves only one filing
        for each group of same `entity_api_id`, `last_end_date` pairs,
        i.e., one filing for each unique enclosure of the same entity
        for the same financial period. If `use_reporting_date` is True,
        grouping is based on `entity_api_id`, `reporting_date` instead.

        Some entities report on multiple markets. If all these
        country-specific filings are wished to retain, set
        `all_markets=True`. Grouping will then also include `country`.

        The selected filing from the group is chosen primarily on
        `languages` parameter values matched on the `language`
        attribute of a `Filing`. Parameter value `['sv', 'fi']` thus
        means that Swedish filings are preferred, secondarily Finnish
        and lastly the ones which have language as `None`. Value `None`
        can be used in the iterable as well. Parameter value `None`
        means no language preference.

        If there are more than one filing for the language match (or
        language=None), the filings will be ordered based on their
        `filing_index` and the last one is chosen which is practically
        the one with highest filing number part of `filing_index`.

        Parameters
        ----------
        languages : iterable of str or None, default ['en']
            Preferred languages for the retained filing.
        use_reporting_date : bool, default False
            Use `reporting_date` instead of `last_end_date` when
            grouping.
        all_markets : bool, default False
            Add `country` to grouping.

        Returns
        -------
        FilingSet
            The set of removed filings.
        """
        if not self.entities.exist:
            msg = 'Entities must be available on the FilingSet'
            raise ValueError(msg)
        if languages is None:
            langs = [None]
        else:
            # Expected type Iterable[None] ?
            langs = list(languages) # type: ignore[arg-type]
        if not any(lan is None for lan in langs):
            langs.append(None)

        enclosures: dict[str, set[Filing]] = {}
        for filing in self:
            key = f'{filing.entity_api_id}'
            if use_reporting_date:
                key += f':{filing.reporting_date}'
            else:
                key += f':{filing.last_end_date}'
            if all_markets:
                key += f':{filing.country}'

            if enclosures.get(key):
                enclosures[key].add(filing)
            else:
                enclosures[key] = {filing}

        popped: set[Filing] = set()
        for enc_filings in enclosures.values():
            # Select correct language filing to be retained
            retain_filing: Union[Filing, None] = None
            for lan in langs:
                lang_filings: set[Filing] = set(filter(
                    lambda f: f.language == lan, enc_filings))
                retain_filing = (
                    self._get_last_filing_index_filing(lang_filings))
                if retain_filing:
                    break
            else:
                # Fallback if no preferred language or None matches
                retain_filing = self._get_last_filing_index_filing(enc_filings)
            # Add the rest to be returned and remove popped from self
            for filing in enc_filings:
                if filing is not retain_filing:
                    popped.add(filing)
        # Execute pop
        self.difference_update(popped)
        return FilingSet(popped)

    def _get_last_filing_index_filing(
            self, filings: set[Filing]
            ) -> Union[Filing, None]:
        if len(filings) == 0:
            return None
        str_indexes = [
            '' if f.filing_index is None else f.filing_index
            for f in filings
            ]
        max_filing_index = max(str_indexes)
        def filter_filing_index_str(filing: Filing) -> bool:
            ismatch = filing.filing_index == max_filing_index
            if not ismatch and max_filing_index == '':
                ismatch = filing.filing_index is None
            return ismatch
        return next(filter(filter_filing_index_str, filings))

    def _get_data_sets(
            self, flags: ScopeFlag
            ) -> tuple[dict[str, Collection[APIResource]], ScopeFlag]:
        """Get sets of data objects and disable flags for empty sets."""
        data_objs: dict[str, Collection[APIResource]] = {'Filing': self}
        subresources = [
            (Entity, self.entities, GET_ENTITY),
            (ValidationMessage, self.validation_messages, GET_VALIDATION_MESSAGES)
            ]
        type_obj: type[APIResource]
        obj_set: ResourceCollection
        for type_obj, obj_set, type_flag in subresources:
            if not obj_set.exist:
                flags &= ~type_obj._FILING_FLAG
            elif type_flag in flags:
                data_objs[type_obj.__name__] = obj_set
        if flags == ScopeFlag(0):
            flags = GET_ONLY_FILINGS
        return data_objs, flags

    @property
    def columns(self) -> list[str]:
        """List of available columns for filings of this set."""
        return Filing.get_columns(
            filings=self,
            has_entities=self.entities.exist
            )

    def __repr__(self) -> str:
        """Return string repr of filing set."""
        subreslist = ''
        if self.entities.exist:
            subreslist += f', len(entities)={len(self.entities)}'
        if self.validation_messages.exist:
            subreslist += (
                f', len(validation_messages)={len(self.validation_messages)}')
        return (
            f'{type(self).__name__}('
            f'len(self)={len(self)}{subreslist})'
            )

    def __contains__(self, item: Any) -> bool:
        """Return `True` if is instance of `Filing` and `api_id` exists."""
        if not isinstance(item, Filing):
            return False
        match_id = item.api_id
        for filing in self:
            if filing.api_id == match_id:
                return True
        return False
