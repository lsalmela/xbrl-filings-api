"""Module for processing SQLite3 databases."""

# SPDX-FileCopyrightText: 2023 Lauri Salmela <lauri.m.salmela@gmail.com>
#
# SPDX-License-Identifier: MIT

# Double quotes are used in all SQL strings by default.
# ruff: noqa: Q000

from __future__ import annotations

import errno
import logging
import os
import sqlite3
from collections.abc import Collection, Sequence
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from xbrl_filings_api import options, order_columns
from xbrl_filings_api.api_resource import APIResource
from xbrl_filings_api.constants import DataAttributeType
from xbrl_filings_api.entity import Entity
from xbrl_filings_api.exceptions import DatabaseSchemaUnmatchError
from xbrl_filings_api.filing import Filing
from xbrl_filings_api.scope_flag import ScopeFlag
from xbrl_filings_api.validation_message import ValidationMessage

__all__ = ['sets_to_sqlite']

logger = logging.getLogger(__name__)

_CurrentSchemaType = dict[str, list[str]]
"""`{'TableName': ['col1', 'col2', ...]}`"""


def sets_to_sqlite(
        flags: ScopeFlag,
        db_path: Path,
        data_objs: dict[str, Collection[APIResource]],
        *,
        update: bool
        ) -> None:
    """
    Save sets to SQLite3 database.

    Raises
    ------
    FileExistsError
    DatabaseSchemaUnmatchError
    sqlite3.DatabaseError
    """
    _validate_path(db_path, update=update)
    _validate_views()
    filing_data_attrs = Filing.get_data_attributes(
        flags, data_objs['Filing'])
    con, table_schema = _create_database_or_extend_schema(
        flags, db_path, filing_data_attrs, update=update)
    _insert_data(table_schema, data_objs, con)
    con.close()


def _validate_path(db_path: Path, *, update: bool) -> None:
    """
    Validate path by raising expections.

    Raises
    ------
    FileExistsError
        When file exists in path and `update` is :pt:`False`.
    """
    if db_path.is_file():
        if not update:
            raise FileExistsError(
                errno.EEXIST,
                os.strerror(errno.EEXIST),
                str(db_path)
                )


def _validate_views():
    used = set()
    if options.views:
        for view in options.views:
            if view.name in used:
                msg = (
                    f'Multiple views in options.views with name "{view.name}"')
                raise ValueError(msg)
            used.add(view.name)


def _create_database_or_extend_schema(
        flags: ScopeFlag,
        db_path: Path,
        filing_data_attrs: list[str],
        *,
        update: bool
        ) -> tuple[sqlite3.Connection, _CurrentSchemaType]:
    """
    Create a new SQLite3 database or extend the database schema.

    When ``update`` is :pt:`True`, any of the tables in existing
    database must match required tables and all of these matching tables
    must have a column ``api_id``.

    Returns
    -------
    sqlite3.Connection
    CurrentSchemaType

    Raises
    ------
    DatabaseSchemaUnmatchError
    sqlite3.DatabaseError
    """
    resource_types: list[type[APIResource]] = [Filing]
    data_attrs = {'Filing': filing_data_attrs}
    if ScopeFlag.GET_ONLY_FILINGS not in flags:
        if ScopeFlag.GET_ENTITY in flags:
            resource_types.append(Entity)
            data_attrs['Entity'] = Entity.get_data_attributes()
        if ScopeFlag.GET_VALIDATION_MESSAGES in flags:
            resource_types.append(ValidationMessage)
            data_attrs['ValidationMessage'] = (
                ValidationMessage.get_data_attributes())

    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    required_table_names = {cls.__name__ for cls in resource_types}
    existing_tables: set[str] = set()
    existing_views: set[str] = set()

    if update:
        _exec(
            cur,
            "SELECT type, name FROM sqlite_schema "
            "WHERE name NOT LIKE 'sqlite_%'"
            )
        db_objs = cur.fetchall()
        existing_tables = {row[1] for row in db_objs if row[0] == 'table'}
        existing_views = {row[1] for row in db_objs if row[0] == 'view'}
        schema_match = False
        for existing_table in existing_tables:
            if existing_table in required_table_names:
                schema_match = True
                break
        if not schema_match:
            path = str(db_path)
            raise DatabaseSchemaUnmatchError(path)

    table_schema: _CurrentSchemaType = {}
    for type_obj in resource_types:
        table_name = type_obj.__name__
        required_columns = data_attrs[table_name]

        col_defs = _get_col_defs(required_columns)
        table_schema[table_name] = [cd[0] for cd in col_defs]

        if table_name in existing_tables:
            existing_cols = _get_existing_column_names(table_name, cur)
            if 'api_id' not in existing_cols:
                path = str(db_path)
                raise DatabaseSchemaUnmatchError(path)
            _add_missing_required_columns(
                table_name, cur, required_columns, existing_cols)
        else:
            _create_new_table(table_name, cur, col_defs)
        connection.commit()

    if options.views:
        _add_compatible_views(cur, existing_views, table_schema)
        connection.commit()
    return connection, table_schema


def _add_missing_required_columns(
        table_name: str, cur: sqlite3.Cursor, required_columns: list[str],
        existing_cols: set[str]):
    add_cols = []
    for col in required_columns:
        if col not in existing_cols:
            add_cols.append(col)
    add_cols = order_columns.order_columns(add_cols)
    for cname, ctype in _get_col_defs(add_cols):
        _exec(
            cur,
            f"ALTER TABLE {table_name} ADD COLUMN {cname} {ctype}"
            )


def _create_new_table(
        table_name: str, cur: sqlite3.Cursor, col_defs: list[tuple[str, str]]):
    _exec(
        cur,
        f"CREATE TABLE {table_name} (\n  "
        + ",\n  ".join(f'{cname} {ctype}' for cname, ctype in col_defs)
        + "\n) WITHOUT ROWID"
        )


def _add_compatible_views(
        cur: sqlite3.Cursor, existing_views: set[str],
        table_schema: _CurrentSchemaType):
    if options.views is None:
        return
    for view in options.views:
        if view.name in existing_views:
            continue
        if not set(view.required_tables).issubset(set(table_schema)):
            continue
        _exec(
            cur,
            f"CREATE VIEW {view.name}\n"
            "AS" + view.sql.rstrip()
            )


def _get_existing_column_names(
        table_name: str, cur: sqlite3.Cursor) -> set[str]:
    _exec(
        cur,
        "SELECT name FROM pragma_table_info(?)",
        (table_name,))
    return set(*zip(*cur.fetchall()))


def _get_col_defs(cols: list[str]) -> list[tuple[str, str]]:
    """Get list of (col_name, type_const)."""
    cols = order_columns.order_columns(cols)
    col_defs = []
    for col in cols:
        type_const = 'TEXT'
        if col.endswith('_count'):
            type_const = 'INTEGER'
        elif col.endswith('_sum') or col.startswith('duplicate_'):
            type_const = 'REAL'
        if col == 'api_id':
            type_const += ' PRIMARY KEY NOT NULL'
        col_defs.append((col, type_const))
    return col_defs


def _insert_data(
        table_schema: _CurrentSchemaType,
        data_objs: dict[str, Collection[APIResource]],
        con: sqlite3.Connection):
    cur = con.cursor()
    for table_name in table_schema:
        cols = table_schema[table_name]
        records: list[tuple[DataAttributeType, ...]] = []
        logger.debug(f'Got {len(data_objs[table_name])} of {table_name}')
        for item in data_objs[table_name]:
            col_data = []
            for col in cols:
                val = None
                if col.endswith('_time') and col != 'query_time':
                    val = getattr(item, f'{col}_str')
                else:
                    val = getattr(item, col)

                # Default date/datetime formatter deprecated in Py3.12
                if isinstance(val, date):
                    val = val.isoformat()

                col_data.append(val)
            records.append(tuple(col_data))
        colsql = '\n  ' + ',\n  '.join(cols) + '\n  '
        phs = ', '.join(['?'] * len(cols))
        _exec(
            cur,
            f"REPLACE INTO {table_name} ({colsql})\nVALUES ({phs})",
            many=records
            )
        con.commit()


def _exec(
        cur: sqlite3.Cursor,
        sql: str,
        params: Sequence[str] = (),
        *,
        many: Optional[Collection[Sequence[DataAttributeType]]] = None
        ) -> None:
    data_len = f' <count: {len(many)}>' if many else ''
    logger.debug(sql + ';' + data_len)

    if many is not None:
        cur.executemany(sql, many)
    else:
        cur.execute(sql, params)


def _adapt_datetime(dt: datetime):
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')


def _adapt_list(list_in: list):
    return '\n'.join(list_in)


sqlite3.register_adapter(datetime, _adapt_datetime)
sqlite3.register_adapter(list, _adapt_list)
