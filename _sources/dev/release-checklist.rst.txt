Release checklist
=================

Documentation
-------------

1. Order ``__all__`` list and objects in modules where it is reasonable.

   a. Expecially `constants`, `debug`, `downloader.stats`, ``enums``,
      `options`.

   b. In `exceptions` module, `FilingsAPIError`, `FilingsAPIWarning`
      should come first, then all exceptions ordered and then warnings
      ordered.

2. Make sure package root ``__init__`` module is up-to-date.

   a. Routine listings of objects match imported objects.

   b. Listing short summaries match the ones in docstrings of objects.

   c. Order of listings follows the one in
      :file:`docs/source/api-reference.rst`.

3. Delete folders :file:`docs/source/ref`, :file:`docs/source/dev/ref`,
   and :file:`docs/build`.

4. Update ``conf.py::release``

5. Check external link integrity (in project shell/project folder):

   .. code-block:: console

        hatch run doc:linkcheck

   Do not care about URIs such as role URI example::

        http://www.example.com/esef/taxonomy/2022-12-31/FinancialPositionConsolidated

6. Go through narrative documentation so that functions and methods work
   as documented.

Final steps
-----------

1. Create ``git`` tag for the release.
