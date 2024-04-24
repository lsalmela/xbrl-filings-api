Using reporting_date or last_end_date
=====================================

The `Filing` objects have two attributes for filing date. These are
`last_end_date` and `reporting_date`.

Attribute last_end_date
-----------------------

The attribute ``last_end_date`` is a data attribute of the filing
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

``last_end_date`` may be on last day of month? api_id=2532
