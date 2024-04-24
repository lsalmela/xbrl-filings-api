Before commit
=============

1. Check formatting with ``ruff`` by running command:

   .. code-block:: console

        hatch fmt -l

2. Check typing with ``mypy`` by running command:

   .. code-block:: console

        hatch run lint:typing

3. Run tests with ``pytest`` by running command:

   .. code-block:: console

        hatch run test

4. Build docs with ``sphinx`` by running command:

   .. code-block:: console

        hatch doc:build