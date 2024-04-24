.. _include parameter: https://jsonapi.org/format/1.0/#fetching-includes
.. _GLEIF foundation search: https://search.gleif.org

Getting started
===============

To avoid unneccesarily long examples, this documentation uses alias
``xf`` for the library. Consequently, it can be expected that all
examples begin::

    import xbrl_filings_api as xf

With regards to :abbr:`ESEF (European Single Electronic Format)`
filings, the term *entity* is used instead of *issuer*, as this is the
term used in the API, the library, and XBRL in general.

Fetching the filings
--------------------

The API natively supports two means of fetching the desired filings.
These are equality-based filtering and sorting. The following query
fetches three oldest Finnish filings in the database using the
`get_filings()` function:

>>> fs = xf.get_filings({'country': 'FI'}, sort='added_time', limit=3)

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
requested:

>>> fs = xf.get_filings({'country': 'FI'}, sort='-added_time', limit=3)

The returned object is a `FilingSet` which is a :class:`set`\ -like
object containing `Filing` objects. All set operations (methods and
operators) are supported and they are not dependent on the filing object
identity. In other words, you can for example take a union of the
results of two separate queries and if they contain same filings, these
filings are handled intuitively, having no duplicates in the output.
However in-place operations (e.g. `FilingSet.intersection_update()`) are
recommended intead of new set operations (e.g.
`FilingSet.intersection()`) to limit the number of deep copied objects.

The library provides convenient :func:`repr` and :class:`str() <str>`
representations for all `APIResource` objects, i.e., filings, entities
and validation messages.

>>> for filing in fs:
...     print(filing)
...
743700PEMBIJ4GPCYX48-2023-12-31-ESEF-FI-0 2023 [fi]
7437004XD6U0FFDCT507-2023-12-31-ESEF-FI-1 2023 [fi]
743700W8ZIJAMXWWWD26-2023-12-31-ESEF-FI-0 2023 [fi]

However, as shown above, querying the sole filings does not reproduce
very easily comprehended ``str()`` values. The above rows show
`Filing.filing_index` instead of `Entity.name`. To see the latter, we
must query again but now including the entities in our results setting
parameter ``flags`` to `GET_ENTITY`:

>>> fs = xf.get_filings({'country': 'FI'}, sort='-added_time', limit=3, flags=xf.GET_ENTITY)
>>> for filing in fs:
...     print(filing)
...
Elecster Oyj 2023 [fi]
Scanfil Oyj 2023 [fi]
Aspocomp Group Oyj 2023 [fi]

The above call to ``get_filings()`` still only produces a single request
to the API but take advantage of the JSON:API `include parameter`_. See
`Filing.__str__` for the full explanation of ``str()`` format.

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

More than one filter can have iterable value. You can find LEI codes for
example with the `GLEIF foundation search`_.

Filings for a financial year
----------------------------

The `Filing` objects have two attributes for the filing date, i.e., the
end of the fiscal year of the reporting period. These are
`last_end_date` and `reporting_date`. For most filings, they are the
same value, but in certain cases they differ. For a detailed
explanation, see :doc:`reporting-date-or-last-end-date`.

What comes to querying, the most pronounced difference is that
``last_end_date`` can be used for querying where as the derived
attribute ``reporting_date`` can not.

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

The scope of the year filter is defined in `options.year_filter_months`
and its default value is::

    ((0, 1),
     (1, 1))

Option ``year_filter_months`` is a tuple of two tuples. The inner tuples
consist of two integers: year offset and month number. The last month is
non-inclusive (as with Python :class:`range() <range>` iterator).
Therefore, the default year filter for ``2022`` returns filings whose
``last_end_date`` is any last day of month from 31 January 2022 until 31
December 2022.

You might also be interested in fiscal years ending around the end of
calendar year. To query Norwegian filings around the end of year 2022
(30 June 2022 to 31 May 2023), use the following:

>>> xf.options.year_filter_months = ((0, 6), (1, 6))
>>> fs = xf.get_filings(
...     filters={'country': 'NO', 'last_end_date': 2022},
...     sort='last_end_date', limit=3, flags=xf.GET_ENTITY)
>>> for filing in fs:
...     print(filing)
...
MEDISTIM ASA 2022 [en]
STOLT-NIELSEN LIMITED Nov-2022 [en]
SAS AB Oct-2022 [sv]

Notice that filing *Navig8 Topco Holdings Inc Mar-2022* disappeared.

To query all month end dates in three years, you can set
``year_filter_months`` to ``((0, 1), (2, 12))``.

It is also possible to filter with month which will make a query to the
last day of the month. The following queries for filings with reporting
period ending on 28 February 2022::

    fs = xf.get_filings({'last_end_date': '2022-02'}, flags=xf.GET_ENTITY)

.. note::

    All fields ending ``'_date'`` can also be queried with
    :class:`datetime.date` objects. Year query can be made with
    ``str`` or ``int`` and month query with ``str``.

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
