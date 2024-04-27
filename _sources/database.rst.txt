Database
========

As of April 2024, the database has filings filed according to the
*European Single Electronic Format* (ESEF), the *United Kingdom Single
Electronic Format* (UKSEF), and the *Ukraine Financial Reporting
System*. The first reports are from financial year 2020 for all
reporting formats.

Annual reports are reported from every country with reports filed. As
for the filings reported in 2022, Danish and Ukrainian filings also
include quarterly reports.

Regarding ESEF, the European Union countries without any filings in the
database are Germany, Ireland, Bulgaria, and Slovakia.

Different language versions of the same report are separate filings.
Sometimes the exactly same report is filed twice due to errors in the
version filed earlier. Use `pop_duplicates()` to get the lastest
reported unique enclosure with language preference. Some entities also
report on multiple markets (different countries/stock exchanges). In the
case of language versions or same market refilings, the reports have the
same `filing_index` except for the entry number (last integer).
