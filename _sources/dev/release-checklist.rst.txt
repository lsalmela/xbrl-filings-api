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

4. Check external link integrity (in project shell/project folder):

   .. code-block:: console

        hatch run doc:linkcheck

   Do not care about URIs such as role URI example::

        http://www.example.com/esef/taxonomy/2022-12-31/FinancialPositionConsolidated

5. Go through narrative documentation so that functions and methods work
   as documented.

6. Update ``xbrl_filings_api/__about__.py::__version__`` and
   ``conf.py::release``.

Final steps
-----------

1. Commit and push last changes to the release. Wait for GitHub Actions
   to run and check results.

2. Create an annotated ``git`` tag for the release::

    git tag -a v<release> -m "Release description."

3. Push the tag::

    git push origin tag v<release>

4. Remove the ``dist`` folder, if it exists.

5. Build the sdist and wheel:

   .. code-block:: console

        hatch build

6. Check the contents of both archives.

7. Publish to PyPI.

   .. code-block:: console

        hatch publish -u __token__ -a pypi-<restofapitoken>
