:og:description: Explanation of basic functionalities of the library using examples

.. _include parameter: https://jsonapi.org/format/1.0/#fetching-includes
.. _GLEIF foundation search: https://search.gleif.org
.. _xBRL-JSON format: https://www.xbrl.org/guidance/xbrl-json-tutorial/

Getting started
===============

To avoid unneccesarily long examples, this documentation uses alias
``xf`` for the library. Consequently, it can be expected that all
examples begin::

    import xbrl_filings_api as xf

With regards to :abbr:`ESEF (European Single Electronic Format)`
filings, the term *entity* is used instead of *issuer*, as this is the
term used in the API, the library, and XBRL in general.

.. _logging:

Logging
-------

If you are running the commands in Python interactive prompt, you may
enable logging on console with the following command::

    import logging, sys
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

The examples below show the output without logging.

Installation
------------

Install the library using pip.

.. code-block:: console

    python -m pip install xbrl-filings-api

Fetching the filings
--------------------

The API natively supports two means of fetching the desired filings.
These are equality-based filtering and sorting. The following query
fetches three oldest Finnish filings in the database using the
`get_filings()` function::

    fs = xf.get_filings({'country': 'FI'}, sort='added_time', limit=3)

The first ``filters`` parameter value demands the API to return only
filings whose field ``'country'`` is the country code of Finland,
``'FI'``. The ``filters`` values are case-sensitive, so requesting
filings with country ``'fi'`` would fetch nothing.

The parameter ``limit`` states the maximum number of filings to
retrieve. Its default value is `NO_LIMIT`. Please be careful with
executing unfiltered and unlimited query calls, the underlying database
is large.

Default sort order is ascending. To reverse the sort order, use minus
sign in the front of the sort field. The latest added records are thus
requested::

    fs = xf.get_filings({'country': 'FI'}, sort='-added_time', limit=3)

The returned object is a `FilingSet` which is a :class:`set`\ -like
object containing `Filing` objects. All set operations (methods and
operators) are supported and they are not dependent on the filing object
identity. In other words, you can make a union of the results of two
separate queries and if they contain same filings, these filings are
handled intuitively, having no duplicates of the same filing in the
union set. However in-place operations (e.g.
`FilingSet.intersection_update()`) are recommended intead of new set
operations (e.g. `FilingSet.intersection()`) to limit the number of deep
copied objects.

The library provides convenient :func:`repr` and :class:`str() <str>`
representations for all `APIResource` objects, i.e., filings, entities,
and validation messages. Use ``repr()`` if you need the unique
identifier ``api_id``.

>>> for filing in fs:
...     print(filing)
...
743700PEMBIJ4GPCYX48-2023-12-31-ESEF-FI-0 2023 [fi]
7437004XD6U0FFDCT507-2023-12-31-ESEF-FI-1 2023 [fi]
743700W8ZIJAMXWWWD26-2023-12-31-ESEF-FI-0 2023 [fi]

However, as shown above, querying the sole filings does not reproduce
very easily comprehended ``str()`` values. The above rows show
`Filing.filing_index` instead of `Entity.name`. To see the latter, we
must query again but now include the entities in our results setting
parameter ``flags`` to `GET_ENTITY`:

>>> fs = xf.get_filings({'country': 'FI'}, sort='-added_time', limit=3, flags=xf.GET_ENTITY)
>>> for filing in fs:
...     print(filing)
...
Elecster Oyj 2023 [fi]
Scanfil Oyj 2023 [fi]
Aspocomp Group Oyj 2023 [fi]

The above call to ``get_filings()`` still only produces a single request
to the API but take advantage of the JSON:API `include parameter`_.

The entity of a filing can be accessed with attribute `Filing.entity`.
To get validation messages, use flag `GET_VALIDATION_MESSAGES`. The
entity and validation message flags can be combined with ``|`` operator,
but a shorthand ``GET_ALL`` also exists. The validation messages can be
then accessed with attribute `Filing.validation_messages`.

See `Filing.__str__`, `Entity.__str__`, and `ValidationMessage.__str__`
for the full explanation of ``str()`` format.

Multifilters
------------

It is possible to query with :term:`iterable` values in a logical ``OR``
style. This will create multiple requests to the API for each value of
the iterable. For example to get the filings of Kone and Nokia for year
2022 by their LEI codes in attribute `Filing.entity.identifier
<identifier>`, query:

>>> fs = xf.get_filings(
...     filters={
...         'entity.identifier': ['2138001CNF45JP5XZK38', '549300A0JPRWG1KI7U06'],
...         'last_end_date': '2022-12-31'},
...     flags=xf.GET_ENTITY)
>>> for filing in fs:
...     print(filing)
...
KONE OYJ 2022 [fi]
KONE OYJ 2022 [en]
Nokia Oyj 2022 [fi]

More than one filter can have an iterable value. You can find LEI codes
for example with the `GLEIF foundation search`_.

Filings for a fiscal year
-------------------------

The `Filing` objects have two attributes for the filing date, i.e., the
end of the fiscal year of the reporting period. Some countries also
report quarterly reports with XBRL (see :doc:`database`). The filing
date attributes are `last_end_date` and `reporting_date`. For most
filings, they are the same value, but in certain cases they differ. For
a detailed explanation, see :doc:`reporting-date-or-last-end-date`.

What comes to querying, the most pronounced difference is that
``last_end_date`` can be used for querying whereas the derived attribute
``reporting_date`` can not.

So, were we interested in querying for Norwegian filings whose reporting
period ends on 31 December 2022, we would use the following call:

>>> fs = xf.get_filings(
...     filters={'country': 'NO', 'last_end_date': '2022-12-31'},
...     limit=3, flags=xf.GET_ENTITY)
>>> for filing in fs:
...     print(filing)
...
ELKEM ASA 2022 [en]
B2HOLDING ASA 2022 [en]
MEDISTIM ASA 2022 [en]

Often, however, the interest is on the filings whose reporting period
ends during the calendar year instead of just last day of December.
We happen to know that *Stolt-Nielsen Limited* has a reporting period
ending on the last day of November, 2022. Thus, we want to use a
*year filter* and only provide a year as the filter value.

>>> fs = xf.get_filings(
...     filters={'country': 'NO', 'last_end_date': 2022},
...     sort='last_end_date', limit=3, flags=xf.GET_ENTITY)
>>> for filing in fs:
...     print(filing)
...
SAS AB Oct-2022 [sv]
Navig8 Topco Holdings Inc Mar-2022
STOLT-NIELSEN LIMITED Nov-2022 [en]

For specialized year filter queries, see
:doc:`changing-year-filter-scope`.

.. note::

    All fields ending ``"_date"`` can also be queried with
    :class:`datetime.date` objects. Year query can be made with either
    ``str`` or ``int``.

Filings for a month
-------------------

It is also possible to filter with month which will make a query to the
last day of the month. The following queries for filings with reporting
period ending on 28 February 2022::

    fs = xf.get_filings({'last_end_date': '2022-02'}, flags=xf.GET_ENTITY)

The following queries for the 2022 second quarter month end dates in
Denmark using a :external:term:`list comprehension`. Notice that leading
zeroes in the month part are not required. This is an alternative to
changing year filter scope.

>>> fs = xf.get_filings(
...     filters={
...         'last_end_date': [f'2022-{mth}' for mth in range(4, 7)],
...         'country': 'DK'},
...     flags=xf.GET_ENTITY)
>>> for filing in fs:
...     print(filing)
... 
Frontmatec Group ApS Jun-2022 [en]
PENNEO A/S Jun-2022 [en]
Gabriel Holding A/S Jun-2022 [da]
(... 70 filings)
Pandora A/S Jun-2022 [en]
ØRSTED A/S Jun-2022 [en]
ISS GLOBAL A/S Jun-2022 [en]

Downloading filings
-------------------

Lets say we have made a successful query and stored the `FilingSet`
object in a variable named ``fs``. We want to save the filings in
`xBRL-JSON format`_ to folder ``'path/to/json'``. We can save them
with the method :meth:`FilingSet.download`::

    fs = xf.get_filings({'country': 'FI'}, sort='-added_time', limit=3)
    fs.download('json', to_dir='path/to/json')

The available download files are listed below. The local path attribute
is set when download is finished. Detailed documentation is found from
URL attribute.

=============  =============  =======================
File string    URL attribute  Local path attribute
=============  =============  =======================
``'json'``     `json_url`     `json_download_path`
``'package'``  `package_url`  `package_download_path`
``'xhtml'``    `xhtml_url`    `xhtml_download_path`
=============  =============  =======================

It is also possible to download multiple types of files at once::

    fs.download(['json', 'package'], to_dir='path/to/json')

We may also override the save folder and define a renaming pattern for
filename using `DownloadItem` objects::

    fs.download({
        'xhtml': xf.DownloadItem(
            stem_pattern='/name/_graphic',
            to_dir='path/to/xhtml'),
        'json': xf.DownloadItem(
            stem_pattern='/name/_data',
            to_dir='path/to/json')
        })

For XHTML report files, the above renames ``'file.xhtml'`` to
``'file_graphic.xhtml'``, saves it to ``'path/to/xhtml'``. The advantage
of the above approach compared to two separate calls is that
``download()`` method downloads files in parallel and a long final
download in the first call would create needless waiting time for the
second call. By default, maximum of 5 parallel downloads are allowed
at any moment during downloading. Change this with parameter
``max_concurrent``.

The `Filing` object also has the same downloading interface::

    filing = next(iter(fs))
    filing.download('json', to_dir='path/to/json')

``Filing`` downloads additionally allow complete renaming of the
downloaded file::

    filing.download(
        {'xhtml': xf.DownloadItem(filename='new_name.html')},
        to_dir='path/to/html')

For timely feedback of finished downloads, methods
`FilingSet.download_aiter()` and `Filing.download_aiter()` return an
asynchronous iterator which yields `DownloadResult` objects. In this
example output, :ref:`logging to sys.stdout is turned on <logging>`.

>>> import asyncio
>>> fs = xf.get_filings({'api_id': ['4143', '8542', '2302']}, flags=xf.GET_ENTITY)
(... log messages)
>>> async def dl_feedback(fs):
...     async for result in fs.download_aiter('package', to_dir='dl_aiter'):
...         if result.err:
...             print(
...                 f'Error downloading {result.info.file} for '
...                 f'{result.info.obj} from {result.url}\n'
...                 f'{result.err}')
...             continue
...         print(
...             f'Downloaded {result.info.file} for {result.info.obj}\n'
...             f'> {result.path}')
... 
>>> asyncio.run(dl_feedback(fs))
WARNING:xbrl_filings_api.download_specs_construct:Package not available for Filing(api_id='8542', entity.name='Приватне Акціонерне Товариство «Рено Україна»', reporting_date=date(2022, 12, 31), language=None)
Downloaded package for SOC CENTRALE BOIS SCIERIES MANCHE Jun-2022 [fr]
> C:\Users\user\path\dl_aiter\SCBSM-2022-06-30-fr.zip
Downloaded package for KONE OYJ 2022 [en]
> C:\Users\user\path\dl_aiter\2138001CNF45JP5XZK38-2022-12-31-EN.zip

The library logs a warning for a missing package file.

Opening filings in web browser
------------------------------

A `Filing` can also be opened in web browser with `open` method. The
default is to open the iXBRL viewer (`viewer_url`).

>>> kone22en = next(f for f in fs if f.entity.name == 'KONE OYJ')
>>> kone22en.open()

The viewer application is sometimes slow to open. If you want to open
the original static XHTML document (`xhtml_url`), set
`options.open_viewer` to :pt:`False`.

>>> xf.options.open_viewer = False
>>> kone22en.open()

Saving objects to SQLite database
---------------------------------

You can export the objects to an SQLite database with function
:func:`~xbrl_filings_api.query.to_sqlite` or method
`FilingSet.to_sqlite()`. The function both queries and inserts the
objects to the database for each page. The method only inserts into a
new database. If you want to update new records to an existing database,
you must set paramter ``update`` to :pt:`True`.

>>> xf.to_sqlite(
...     path='filings.sqlite',
...     filters={'country': 'FI', 'last_end_date': '2022-12'},
...     flags=xf.GET_ALL)

A few `SQLite views <default_views>` are also included in the database
by default.

Exporting objects to pandas dataframe
-------------------------------------

It is possible to generate a dict for :class:`pandas.DataFrame` ``data``
attribute with methods `FilingSet.get_pandas_data()` and
`ResourceCollection.get_pandas_data()`. To get a dataframe for
validation messages. The attributes ending ``_url`` are not included by
default:

>>> import pandas as pd
>>> fs = xf.get_filings({'country': 'FI'}, sort='-added_time', limit=3, flags=xf.GET_ALL)
>>> vm_data = fs.validation_messages.get_pandas_data()
>>> df = pd.DataFrame(vm_data)

Filtering out redundant languages
---------------------------------

You can filter out redundant language versions of the same filing with
`pop_duplicates()`. By default, it prefers filings in English. To get
filings preferably in English and secondarily in Finnish:

>>> fs.pop_duplicates(['en', 'fi'])

Explicit paging
---------------

It is possible to handle the pages explicitly with function
`filing_page_iter`. The order of filings on a page is then retained as
they are returned in a list. The iterator is lazy and makes requests to
the API only when next page is called. As with other query functions,
the maximum page size can be controlled with `options.max_page_size`.

>>> xf.options.max_page_size = 3
>>> page_iter = xf.filing_page_iter({'country': 'SE'}, sort='-added_time', flags=xf.GET_ENTITY)
>>> for page in page_iter:
...     for filing in page.filing_list:
...         print(filing)
...     break
...
MedCap AB (publ) 2023 [sv]
Ortivus Aktiebolag 2023 [sv]
AddLife AB 2023 [sv]

In rare occasions the API returns the same filing on a subsequent page.
For this reason it must not be relied upon that every page before the
last has exactly ``max_page_size`` filings as the same filing is always
returned once.

Query match size
----------------

It is possible to get the number of filings matched by the query without
going through all the pages with function `filing_page_iter`. To see how
many filings there are in the database filed in Sweden you can use
attribute `FilingsPage.query_filing_count`::

>>> page = next(xf.filing_page_iter({'country': 'SE'}, limit=1))
>>> print(f'{page.query_filing_count} filings from Sweden')

APIObject inheritance hierarchy
-------------------------------

::

    APIObject
        APIResource
            Filing
            Entity
            ValidationMessage
        APIPage
            FilingsPage
        APIError
