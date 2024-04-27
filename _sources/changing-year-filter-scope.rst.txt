Changing year filter scope
==========================

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

To query all month end dates in three years, you can set
``year_filter_months`` to ``((0, 1), (3, 1))``.
