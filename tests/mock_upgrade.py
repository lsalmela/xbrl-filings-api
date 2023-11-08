"""
Fetch mock URLs for tests and save them.

This module is a standalone script and it is not available for
importing.

The fetched URLs will be saved to YAML files in directory
`MOCK_URL_DIR_NAME` inside `tests` package.

.. note::
    This script uses beta feature `responses._recorder` (as of
    `responses` version 0.23.3).
"""

# SPDX-FileCopyrightText: 2023 Lauri Salmela <lauri.m.salmela@gmail.com>
#
# SPDX-License-Identifier: MIT

import argparse
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import requests
from responses import _recorder

MOCK_URL_DIR_NAME = 'mock_responses'
CONFTEST_SRC_PATH = 'conftest_source.py'
CONFTEST_OUT_PATH = 'conftest.py'
ENTRY_POINT_URL = 'https://filings.xbrl.org/api/filings'

conftest_src_spath = str(Path(__file__).parent / CONFTEST_SRC_PATH)
conftest_out_spath = str(Path(__file__).parent / CONFTEST_OUT_PATH)
mock_dir_path = Path(__file__).parent / MOCK_URL_DIR_NAME
JSON_API_HEADERS = {
    'Content-Type': 'application/vnd.api+json'
    }
REQUEST_TIMEOUT = 30.0

URL_MOCK_FIXTURE_TEMPLATE = '''
@pytest.fixture
def {fixt_name}_response():
    """{docstring}"""
    with responses.RequestsMock({param_str}) as rsps:
        rsps._add_from_file(_get_path('{name}'))
        yield rsps
'''
URL_MOCK_PARAM_LAX = 'assert_all_requests_are_fired=False'
NO_EDIT_DOCSTRING = '''
DO NOT EDIT: This module is automatically generated by the script
``mock_upgrade.py``. Edit file ``conftest_source.py`` instead and run
the aforementioned script.
'''

urlmock = {}


@dataclass
class _URLMock:
    name: str
    """Name of the mock URL collection."""
    fetch: Callable
    """Function to fetch and save the URL mock collection."""
    lax_fixture: bool
    """
    Also create a fixture with a name ``<name>_lax``.

    The lax version of the fixture adds parameter
    ``assert_all_requests_are_fired=False`` to initiation of
    `responses.RequestsMock`. These fixtures are used when the test
    function should raise (other than APIError) and not necessarily
    initiate all of the URL request.
    """
    isfetch: bool = True
    """Should this mock be fetched."""


def _get_path(mock_name):
    """Get absolute file path of the mock URL collection file."""
    file_path = mock_dir_path / f'{mock_name}.yaml'
    return str(file_path)


def _addmock(name, lax_fixture=False):  # noqa: FBT002
    urlmock[name] = _URLMock(
        name=name,
        fetch=globals()[f'_fetch_{name}'],
        lax_fixture=lax_fixture
        )


###################### DEFINE MOCK URL COLLECTIONS #####################


@_recorder.record(file_path=_get_path('creditsuisse21en_by_id'))
def _fetch_creditsuisse21en_by_id():
    """Credit Suisse 2021 English AFR filing by `api_id`."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 1,
            # id = api_id
            'filter[id]': '162',
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('creditsuisse21en_by_id')


@_recorder.record(file_path=_get_path('asml22en'))
def _fetch_asml22en():
    """ASML Holding 2022 English AFR filing."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 1,
            # fxo_id = filing_index
            'filter[fxo_id]': '724500Y6DUVHQD6OXN27-2022-12-31-ESEF-NL-0',
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('asml22en')


@_recorder.record(file_path=_get_path('asml22en_entities'))
def _fetch_asml22en_entities():
    """ASML Holding 2022 English AFR filing with entity."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 1,
            # fxo_id = filing_index
            'filter[fxo_id]': '724500Y6DUVHQD6OXN27-2022-12-31-ESEF-NL-0',
            'include': 'entity'
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('asml22en_entities')


@_recorder.record(file_path=_get_path('asml22en_vmessages'))
def _fetch_asml22en_vmessages():
    """ASML Holding 2022 English AFR filing with validation messages."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 1,
            'include': 'validation_messages',
            # fxo_id = filing_index
            'filter[fxo_id]': '724500Y6DUVHQD6OXN27-2022-12-31-ESEF-NL-0'
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('asml22en_vmessages')


@_recorder.record(file_path=_get_path('asml22en_ent_vmsg'))
def _fetch_asml22en_ent_vmsg():
    """ASML Holding 2022 English AFR filing with entities and v-messages."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 1,
            # fxo_id = filing_index
            'filter[fxo_id]': '724500Y6DUVHQD6OXN27-2022-12-31-ESEF-NL-0',
            'include': 'entity,validation_messages'
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('asml22en_ent_vmsg')


@_recorder.record(file_path=_get_path('filter_language'))
def _fetch_filter_language():
    """Filter by language 'fi'."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 1,
            'filter[language]': 'fi',
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('filter_language')


@_recorder.record(file_path=_get_path('filter_last_end_date'))
def _fetch_filter_last_end_date():
    """Filter by last_end_date '2021-02-28'."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 1,
            'filter[period_end]': '2021-02-28', # last_end_date
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('filter_last_end_date', lax_fixture=True)


@_recorder.record(file_path=_get_path('filter_error_count'))
def _fetch_filter_error_count():
    """Filter by error_count value 1."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 1,
            'filter[error_count]': 1
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('filter_error_count')


@_recorder.record(file_path=_get_path('filter_added_time'))
def _fetch_filter_added_time():
    """Filter by added_time value '2021-09-23 00:00:00'."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 1,
            'filter[date_added]': '2021-09-23 00:00:00' # added_time
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('filter_added_time', lax_fixture=True)


@_recorder.record(file_path=_get_path('filter_added_time_2'))
def _fetch_filter_added_time_2():
    """Filter by added_time value '2023-05-09 13:27:02.676029'."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 1,
            'filter[date_added]': '2023-05-09 13:27:02.676029' # added_time
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('filter_added_time_2', lax_fixture=True)


@_recorder.record(file_path=_get_path('filter_entity_api_id'))
def _fetch_filter_entity_api_id():
    """Return error when filtering with `entity_api_id`."""
    kone_id = '2499'
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 1,
            'filter[entity_api_id]': kone_id
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('filter_entity_api_id', lax_fixture=True)


@_recorder.record(file_path=_get_path('filter_package_url'))
def _fetch_filter_package_url():
    """Filter by package_url of Kone 2022 filing."""
    filter_url = (
        '/2138001CNF45JP5XZK38/2022-12-31/ESEF/FI/0/'
        '2138001CNF45JP5XZK38-2022-12-31-EN.zip'
        )
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 1,
            'filter[package_url]': filter_url
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('filter_package_url')


@_recorder.record(file_path=_get_path('filter_package_sha256'))
def _fetch_filter_package_sha256():
    """Filter by package_sha256 of Kone 2022 filing."""
    filter_sha = (
        'e489a512976f55792c31026457e86c9176d258431f9ed645451caff9e4ef5f80')
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 1,
            'filter[sha256]': filter_sha # package_sha256
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('filter_package_sha256')


@_recorder.record(file_path=_get_path('finnish_jan22'))
def _fetch_finnish_jan22():
    """Finnish AFR filings with reporting period ending in Jan 2022."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 2,
            'filter[country]': 'FI',
            'filter[period_end]': '2022-01-31' # last_end_date
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('finnish_jan22')


@_recorder.record(file_path=_get_path('oldest3_fi'))
def _fetch_oldest3_fi():
    """Oldest 3 AFR filings reported in Finland."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 3,
            'filter[country]': 'FI',
            'sort': 'date_added' # added_time
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('oldest3_fi')


@_recorder.record(file_path=_get_path('sort_two_fields'))
def _fetch_sort_two_fields():
    """
    Sort Finnish filings by `last_end_date` and `added_time`.

    .. warning::

        Volatile with ``mock_upgrade.py`` run. See test
        ``test_query::Test_get_filings::test_sort_two_fields``.
    """
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 2,
            'filter[country]': 'FI',
            'sort': 'period_end,processed' # last_end_date, processed_time
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('sort_two_fields')


@_recorder.record(file_path=_get_path('multipage'))
def _fetch_multipage():
    """Get 3 pages (2pc) of oldest Swedish filings."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 2,
            'filter[country]': 'SE',
            'sort': 'date_added' # added_time
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 2,
            'filter[country]': 'SE',
            'sort': 'date_added', # added_time
            'page[number]': 2
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 2,
            'filter[country]': 'SE',
            'sort': 'date_added', # added_time
            'page[number]': 3
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('multipage', lax_fixture=True)


@_recorder.record(file_path=_get_path('api_id_multifilter'))
def _fetch_api_id_multifilter():
    """Get 4 Shell filings for 2021 and 2022."""
    for id_i, api_id in enumerate(('1134', '1135', '4496', '4529')):
        _ = requests.get(
            url=ENTRY_POINT_URL,
            params={
                'page[size]': 4 - id_i,
                'filter[id]': api_id
                },
            headers=JSON_API_HEADERS,
            timeout=REQUEST_TIMEOUT
            )
_addmock('api_id_multifilter')


@_recorder.record(file_path=_get_path('country_multifilter'))
def _fetch_country_multifilter():
    """Get three filings for the first country `FI`."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 3,
            'filter[country]': 'FI'
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('country_multifilter')


@_recorder.record(file_path=_get_path('filing_index_multifilter'))
def _fetch_filing_index_multifilter():
    """Get three filings for the first country `FI`."""
    fxo_codes = (
        '21380068P1DRHMJ8KU70-2021-12-31-ESEF-GB-0',
        '21380068P1DRHMJ8KU70-2021-12-31-ESEF-NL-0'
        )
    for fxo_i, fxo in enumerate(fxo_codes):
        _ = requests.get(
            url=ENTRY_POINT_URL,
            params={
                'page[size]': 2 - fxo_i,
                'filter[fxo_id]': fxo # filing_index
                },
            headers=JSON_API_HEADERS,
            timeout=REQUEST_TIMEOUT
            )
_addmock('filing_index_multifilter')


@_recorder.record(file_path=_get_path('reporting_date_multifilter'))
def _fetch_reporting_date_multifilter():
    """Return an error for filtering with `reporting_date`."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 3,
            'filter[reporting_date]': '2020-12-31'
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('reporting_date_multifilter')


@_recorder.record(file_path=_get_path('inconsistency_count_multifilter'))
def _fetch_inconsistency_count_multifilter():
    """Return an error for filtering with `inconsistency_count`."""
    _ = requests.get(
        url=ENTRY_POINT_URL,
        params={
            'page[size]': 2,
            'filter[inconsistency_count]': 1
            },
        headers=JSON_API_HEADERS,
        timeout=REQUEST_TIMEOUT
        )
_addmock('inconsistency_count_multifilter')


@_recorder.record(file_path=_get_path('processed_time_multifilter'))
def _fetch_processed_time_multifilter():
    """Get two filings filtered with `processed_time`."""
    cloetta_sv_strs = (
        '2023-01-18 11:02:06.724768',
        '2023-05-16 21:07:17.825836'
        )
    for filter_i, filter_str in enumerate(cloetta_sv_strs):
        _ = requests.get(
            url=ENTRY_POINT_URL,
            params={
                'page[size]': 2 - filter_i,
                'filter[processed]': filter_str # processed_time
                },
            headers=JSON_API_HEADERS,
            timeout=REQUEST_TIMEOUT
            )
_addmock('processed_time_multifilter')


################ END OF MOCK URL COLLECTION DEFINITIONS ################


def main():
    """Run the command line interface."""
    parser = argparse.ArgumentParser(
        description=(
            'Script for updating mock URL collections for tests in '
            f'folder "{MOCK_URL_DIR_NAME}".'
            ),
        epilog=(
            'If no flags are given, default behavior is to upgrade all '
            'mock URL collections.'
            )
        )

    parser.add_argument(
        '-l', '--list', action='store_true',
        help='list all mocks defined in this module'
        )
    parser.add_argument(
        '-b', '--bare-list', action='store_true',
        help='use simple bare list format with --list'
        )
    parser.add_argument(
        '-n', '--new', action='store_true',
        help='upgrade only new, unfetched mock URL collections'
        )

    clargs = parser.parse_args()

    if clargs.list:
        _list_mock_urls(clargs.bare_list)
    elif clargs.new:
        _upgrade_mock_urls(only_new=True)
    else:
        _upgrade_mock_urls(only_new=False)


def _upgrade_mock_urls(only_new):
    # Ensure directory exists
    mock_dir_path.mkdir(parents=True, exist_ok=True)

    fetch_count = len(urlmock)
    if only_new:
        fetch_count = _flag_new_for_fetching()
        print(
            f'\nUpgrading {fetch_count} unfetched mock URL '
            'collection(s)\n'
            )
    else:
        print(
            f'\nUpgrading all {fetch_count} mock URL collections\n')

    # Run recorder functions
    with open(conftest_out_spath, 'w', encoding='utf-8') as ctout:

        # Write non-generated conftest.py contents
        with open(conftest_src_spath, 'r', encoding='utf-8') as ctsource:
            skip_until_newline = False
            for line in ctsource:
                if skip_until_newline:
                    skip_until_newline = line != '\n'
                elif line.startswith('EDITABLE: '):
                    ctout.write(NO_EDIT_DOCSTRING.lstrip() + '\n')
                    skip_until_newline = True
                else:
                    ctout.write(line)

        # Iterate URL mock collections, download and save request
        # contents and append conftext.py accordingly
        for mock in urlmock.values():
            py_code = _mock_url_to_py_code(mock)
            ctout.write('\n' + py_code)

            if not mock.isfetch:
                continue
            print(f'> {mock.name}')
            mock.fetch()

    _delete_files_of_removed_mocks()

    if only_new:
        print(f'\nFetched {fetch_count} new mock(s)')
    else:
        print('\nFetched all mocks')
    print(f'\nUpdated "{CONFTEST_OUT_PATH}"')
    print(f'\nFolder path: {mock_dir_path}')


def _mock_url_to_py_code(mock):
    """Write generated conftest.py contents for URL mock collections."""
    gen_py_list = []
    for islax in range(2 if mock.lax_fixture else 1):
        fixt_name = mock.name
        param_str = ''
        if islax:
            fixt_name = f'{fixt_name}_lax'
            param_str = URL_MOCK_PARAM_LAX
        gen_py_list.append(
            URL_MOCK_FIXTURE_TEMPLATE.format(
                name=mock.name,
                fixt_name=fixt_name,
                docstring=mock.fetch.__doc__,
                param_str=param_str
                ))
    return '\n'.join(gen_py_list)


def _list_mock_urls(bare_list):
    new_count = _flag_new_for_fetching()
    new_text = f' ({new_count} new)' if new_count else ''
    if not bare_list:
        print(f'\nFound {len(urlmock)} mock URL collections{new_text}:')
    for mock in urlmock.values():
        if bare_list:
            print(mock.name)
        else:
            print('\n' + mock.name, end='')
            par_parts = []
            if mock.lax_fixture:
                par_parts.append('lax available')
            if mock.isfetch:
                par_parts.append('unfetched')
            if par_parts:
                print(' (' + ', '.join(par_parts) + ')')
            else:
                print()
            print(f'    {mock.fetch.__doc__.strip()}')


def _delete_files_of_removed_mocks():
    mock_names = set(urlmock.keys())
    deleted_files = []
    for filepath in mock_dir_path.iterdir():
        if filepath.stem not in mock_names:
            filepath.unlink()
            deleted_files.append(filepath.name)
    if deleted_files:
        print('\nDeleted files of removed mocks in following files:\n')
        for filename in deleted_files:
            print(f'{MOCK_URL_DIR_NAME}/{filename}')


def _flag_new_for_fetching():
    existing_count = 0
    for mock in urlmock.values():
        mock_path = mock_dir_path / f'{mock.name}.yaml'
        if mock_path.is_file():
            mock.isfetch = False
            existing_count += 1
    return len(urlmock) - existing_count


if __name__ == '__main__':
    main()
else:
    msg = 'This module must be run as a script.'
    raise NotImplementedError(msg)
