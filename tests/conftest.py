"""
Configure `pytest` library.

DO NOT EDIT: This module is automatically generated by the script
``mock_upgrade.py``. Edit file ``conftest_source.py`` instead and run
the aforementioned script.

.. note::
    This script uses beta feature `responses._add_from_file` (as of
    `responses` version 0.23.3).
"""

# SPDX-FileCopyrightText: 2023 Lauri Salmela <lauri.m.salmela@gmail.com>
#
# SPDX-License-Identifier: MIT

import hashlib
from pathlib import Path
from typing import Union

import pytest
import responses

import xbrl_filings_api as xf
from xbrl_filings_api import FilingSet, ResourceCollection

MOCK_URL_DIR_NAME = 'mock_responses'

mock_dir_path = Path(__file__).parent / MOCK_URL_DIR_NAME


def _get_path(set_id):
    """Get absolute file path of the mock URL collection file."""
    file_path = mock_dir_path / f'{set_id}.yaml'
    return str(file_path)


@pytest.fixture
def filings() -> FilingSet:
    """Return FilingSet."""
    return FilingSet()


@pytest.fixture
def res_colls(filings) -> dict[str, ResourceCollection]:
    """Return subresource collections for filings fixture."""
    return {
        'Entity': filings.entities,
        'ValidationMessage': filings.validation_messages
        }


@pytest.fixture(scope='package')
def db_record_count():
    """Function for getting total count of Filing database table."""
    def _db_record_count(cur):
        cur.execute("SELECT COUNT(*) FROM Filing")
        return cur.fetchone()[0]
    return _db_record_count


@pytest.fixture(scope='module')
def mock_response_data():
    """Arbitrary data to mock download."""
    return '0123456789' * 100


@pytest.fixture(scope='module')
def mock_response_sha256(mock_response_data):
    """SHA-256 hash for `mock_response_data`."""
    fhash = hashlib.sha256(
        string=mock_response_data.encode(encoding='utf-8'),
        usedforsecurity=False
        )
    return fhash.hexdigest()


@pytest.fixture(scope='module')
def mock_url_response(mock_response_data):
    """Function to add a `responses` mock URL with `mock_response_data` body."""
    def _mock_url_response(
            url: str, rsps: Union[responses.RequestsMock, None] = None):
        nonlocal mock_response_data
        if rsps is None:
            rsps = responses
        rsps.add(
            method=responses.GET,
            url=url,
            body=mock_response_data,
            headers={}
            )
    return _mock_url_response


@pytest.fixture(scope='package')
def get_oldest3_fi_filingset():
    """Get FilingSet from mock response ``oldest3_fi``."""
    def _get_oldest3_fi_filingset():
        fs = None
        with responses.RequestsMock() as rsps:
            rsps._add_from_file(_get_path('oldest3_fi'))
            fs = xf.get_filings(
                filters={'country': 'FI'},
                sort='date_added',
                max_size=3,
                flags=xf.GET_ONLY_FILINGS,
                add_api_params=None
                )
        return fs
    return _get_oldest3_fi_filingset


@pytest.fixture(scope='package')
def get_oldest3_fi_entities_filingset():
    """Get FilingSet from mock response ``oldest3_fi_entities`` with entities."""
    def _get_oldest3_fi_entities_filingset():
        fs = None
        with responses.RequestsMock() as rsps:
            rsps._add_from_file(_get_path('oldest3_fi_entities'))
            fs = xf.get_filings(
                filters={'country': 'FI'},
                sort='date_added',
                max_size=3,
                flags=xf.GET_ENTITY,
                add_api_params=None
                )
        return fs
    return _get_oldest3_fi_entities_filingset


@pytest.fixture(scope='package')
def get_oldest3_fi_vmessages_filingset():
    """Get FilingSet from mock response ``oldest3_fi_vmessages`` with validation messages."""
    def _get_oldest3_fi_vmessages_filingset():
        fs = None
        with responses.RequestsMock() as rsps:
            rsps._add_from_file(_get_path('oldest3_fi_vmessages'))
            fs = xf.get_filings(
                filters={'country': 'FI'},
                sort='date_added',
                max_size=3,
                flags=xf.GET_VALIDATION_MESSAGES,
                add_api_params=None
                )
        return fs
    return _get_oldest3_fi_vmessages_filingset


@pytest.fixture(scope='package')
def get_oldest3_fi_ent_vmessages_filingset():
    """Get FilingSet from mock response ``oldest3_fi_ent_vmessages`` with entities and validation messages."""
    def _get_oldest3_fi_ent_vmessages_filingset():
        fs = None
        with responses.RequestsMock() as rsps:
            rsps._add_from_file(_get_path('oldest3_fi_ent_vmessages'))
            fs = xf.get_filings(
                filters={'country': 'FI'},
                sort='date_added',
                max_size=3,
                flags=(xf.GET_ENTITY | xf.GET_VALIDATION_MESSAGES),
                add_api_params=None
                )
        return fs
    return _get_oldest3_fi_ent_vmessages_filingset


@pytest.fixture
def creditsuisse21en_by_id_response():
    """Credit Suisse 2021 English AFR filing by `api_id`."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('creditsuisse21en_by_id'))
        yield rsps


@pytest.fixture
def creditsuisse21en_by_id_entity_response():
    """Credit Suisse 2021 English AFR filing by `api_id` and with Entity."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('creditsuisse21en_by_id_entity'))
        yield rsps


@pytest.fixture
def asml22en_response():
    """ASML Holding 2022 English AFR filing."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('asml22en'))
        yield rsps


@pytest.fixture
def asml22en_entities_response():
    """ASML Holding 2022 English AFR filing with entity."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('asml22en_entities'))
        yield rsps


@pytest.fixture
def asml22en_vmessages_response():
    """ASML Holding 2022 English AFR filing with validation messages."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('asml22en_vmessages'))
        yield rsps


@pytest.fixture
def assicurazioni21it_vmessages_response():
    """Assicurazioni Generali 2021 Italian AFR filing with validation messages."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('assicurazioni21it_vmessages'))
        yield rsps


@pytest.fixture
def tecnotree21fi_vmessages_response():
    """Tecnotree 2021 Finnish AFR filing with validation messages."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('tecnotree21fi_vmessages'))
        yield rsps


@pytest.fixture
def asml22en_ent_vmsg_response():
    """ASML Holding 2022 English AFR filing with entities and v-messages."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('asml22en_ent_vmsg'))
        yield rsps


@pytest.fixture
def filter_language_response():
    """Filter by language 'fi'."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('filter_language'))
        yield rsps


@pytest.fixture
def filter_last_end_date_response():
    """Filter by last_end_date '2021-02-28'."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('filter_last_end_date'))
        yield rsps


@pytest.fixture
def filter_last_end_date_lax_response():
    """Filter by last_end_date '2021-02-28'."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps._add_from_file(_get_path('filter_last_end_date'))
        yield rsps


@pytest.fixture
def filter_error_count_response():
    """Filter by error_count value 0."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('filter_error_count'))
        yield rsps


@pytest.fixture
def filter_inconsistency_count_response():
    """Filter by `inconsistency_count` value 0."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('filter_inconsistency_count'))
        yield rsps


@pytest.fixture
def filter_warning_count_response():
    """Filter by warning_count value 0."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('filter_warning_count'))
        yield rsps


@pytest.fixture
def filter_added_time_response():
    """Filter by added_time value '2021-09-23 00:00:00'."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('filter_added_time'))
        yield rsps


@pytest.fixture
def filter_added_time_lax_response():
    """Filter by added_time value '2021-09-23 00:00:00'."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps._add_from_file(_get_path('filter_added_time'))
        yield rsps


@pytest.fixture
def filter_added_time_2_response():
    """Filter by added_time value '2023-05-09 13:27:02.676029'."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('filter_added_time_2'))
        yield rsps


@pytest.fixture
def filter_entity_api_id_response():
    """Return error when filtering with `entity_api_id`."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('filter_entity_api_id'))
        yield rsps


@pytest.fixture
def filter_entity_api_id_lax_response():
    """Return error when filtering with `entity_api_id`."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps._add_from_file(_get_path('filter_entity_api_id'))
        yield rsps


@pytest.fixture
def filter_json_url_response():
    """Filter by json_url of Kone 2022 [en] filing."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('filter_json_url'))
        yield rsps


@pytest.fixture
def filter_package_url_response():
    """Filter by package_url of Kone 2022 [en] filing."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('filter_package_url'))
        yield rsps


@pytest.fixture
def filter_viewer_url_response():
    """Filter by viewer_url of Kone 2022 [en] filing."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('filter_viewer_url'))
        yield rsps


@pytest.fixture
def filter_xhtml_url_response():
    """Filter by xhtml_url of Kone 2022 [en] filing."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('filter_xhtml_url'))
        yield rsps


@pytest.fixture
def filter_package_sha256_response():
    """Filter by package_sha256 of Kone 2022 filing."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('filter_package_sha256'))
        yield rsps


@pytest.fixture
def finnish_jan22_response():
    """Finnish AFR filings with reporting period ending in Jan 2022."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('finnish_jan22'))
        yield rsps


@pytest.fixture
def oldest3_fi_response():
    """Oldest 3 AFR filings reported in Finland."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('oldest3_fi'))
        yield rsps


@pytest.fixture
def oldest3_fi_entities_response():
    """Oldest 3 AFR filings reported in Finland with entities."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('oldest3_fi_entities'))
        yield rsps


@pytest.fixture
def oldest3_fi_vmessages_response():
    """Oldest 3 AFR filings reported in Finland with validation messages."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('oldest3_fi_vmessages'))
        yield rsps


@pytest.fixture
def oldest3_fi_ent_vmessages_response():
    """Oldest 3 AFR filings reported in Finland with entities and validation messages."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('oldest3_fi_ent_vmessages'))
        yield rsps


@pytest.fixture
def sort_two_fields_response():
    """
    Sort Finnish filings by `last_end_date` and `added_time`.

    .. warning::

        Volatile with ``mock_upgrade.py`` run. See test
        ``test_query_sort::test_sort_two_fields``.
    """
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('sort_two_fields'))
        yield rsps


@pytest.fixture
def paging_swedish_size2_pg3_response():
    """Get 3 pages, actually 4, (pg size 2) of oldest Swedish filings."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('paging_swedish_size2_pg3'))
        yield rsps


@pytest.fixture
def paging_swedish_size2_pg3_lax_response():
    """Get 3 pages, actually 4, (pg size 2) of oldest Swedish filings."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps._add_from_file(_get_path('paging_swedish_size2_pg3'))
        yield rsps


@pytest.fixture
def multifilter_api_id_response():
    """Get 4 Shell filings for 2021 and 2022."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('multifilter_api_id'))
        yield rsps


@pytest.fixture
def multifilter_country_response():
    """Get three filings for the first country `FI`."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('multifilter_country'))
        yield rsps


@pytest.fixture
def multifilter_filing_index_response():
    """Get three filings for the first country `FI`."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('multifilter_filing_index'))
        yield rsps


@pytest.fixture
def multifilter_reporting_date_response():
    """Return an error for filtering with `reporting_date`."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('multifilter_reporting_date'))
        yield rsps


@pytest.fixture
def multifilter_processed_time_response():
    """Get two filings filtered with `processed_time`."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('multifilter_processed_time'))
        yield rsps


@pytest.fixture
def unknown_filter_error_response():
    """Get an error of unknown filter."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('unknown_filter_error'))
        yield rsps


@pytest.fixture
def bad_page_error_response():
    """Get an error of page number -1."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('bad_page_error'))
        yield rsps


@pytest.fixture
def fortum23fi_xhtml_language_response():
    """Fortum 2023 Finnish AFR filing with language in xhtml_url."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('fortum23fi_xhtml_language'))
        yield rsps


@pytest.fixture
def paging_czechia20dec_response():
    """Czech 2020-12-31 AFRs."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('paging_czechia20dec'))
        yield rsps


@pytest.fixture
def multifilter_belgium20_short_date_year_response():
    """Belgian 2020 AFRs querying with short date filter year, max_size=100."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('multifilter_belgium20_short_date_year'))
        yield rsps


@pytest.fixture
def multifilter_belgium20_short_date_year_no_limit_response():
    """Belgian 2020 AFRs querying with short date filter year, max_size=NO_LIMIT, options.max_page_size=200."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('multifilter_belgium20_short_date_year_no_limit'))
        yield rsps


@pytest.fixture
def sort_asc_package_sha256_latvia_response():
    """Sorted ascending by package_sha256 from Latvian records."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('sort_asc_package_sha256_latvia'))
        yield rsps


@pytest.fixture
def sort_desc_package_sha256_latvia_response():
    """Sorted ascending by package_sha256 from Latvian records."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('sort_desc_package_sha256_latvia'))
        yield rsps


@pytest.fixture
def kone22_all_languages_response():
    """Sorted ascending by package_sha256 from Latvian records."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('kone22_all_languages'))
        yield rsps


@pytest.fixture
def estonian_2_pages_3_each_response():
    """Estonian filings 2 pages of size 3, incl. entities, v-messages."""
    with responses.RequestsMock() as rsps:
        rsps._add_from_file(_get_path('estonian_2_pages_3_each'))
        yield rsps
