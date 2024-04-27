.. _ESEF Reporting Manual: https://www.esma.europa.eu/sites/default/files/library/esma32-60-254_esef_reporting_manual.pdf

Using reporting_date or last_end_date
=====================================

The `Filing` objects have two attributes for filing date. These are
`last_end_date` and `reporting_date`.

Attribute last_end_date
-----------------------

The attribute `last_end_date` is a data attribute of the filing
returned from the API. It can be used for filtering and sorting. The
attribute has been renamed in this library from the original name
``period_end``.

The value represents the tagged value (XBRL fact) on the report with the
latest instant [#bsinfo]_ or ending [#icfinfo]_ date. Typically this
date represents the actual end of the reporting period.

There are, however, situations when ``last_end_date`` records dates
later than the end of reporting period. Many of these are tagging errors
(cf. ``api_id='6596'``, last_end_date is end of year 4172). Some are
vague dates for proposed and not yet recognized
dividends [#propdividend]_ such as date referring to shareholder meeting
approval instead of reporting period end (``api_id='12983'``) or dated
on the decision day of paying interim dividends (``api_id='12392'``).

.. [#bsinfo] Balance sheet style date information
.. [#icfinfo] Income and cash flow statement style date information
.. [#propdividend] IFRS taxonomy line item ``ifrs-full:DividendsProposedOrDeclaredBeforeFinancialStatementsAuthorisedForIssueButNotRecognisedAsDistributionToOwners``

Attribute reporting_date
------------------------

The attribute `reporting_date` has been derived from the filename in
`package_url` and `last_end_date`, and falls back to using
`last_end_date` if neither could be resolved. This is the file naming
convention used in ESEF reporting (`ESEF Reporting Manual`_,
Guidance 2.6.3). There are mistakes in the filenames as well, but
technical issues such as very lately dated tagged facts do not interfere
with it.

A major caveat with this value is that as a field derived by the
library, it cannot be used in filtering and sorting the query.
