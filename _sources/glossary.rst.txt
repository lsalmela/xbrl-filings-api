Glossary
========

.. glossary::

    collection
        An object which is :term:`iterable`, has a length and can be
        tested with 'in' operator. Abstract base class defined in
        `collections.abc.Collection`.

    iterable
        An object which can be iterated over (e.g. in a ``for .. in``
        loop). Abstract base class defined in
        `collections.abc.Iterable`.

    mapping
        An dict-like object which behaves like a :term:`collection`, can
        be accessed with indexer syntax (:pt:`obj[key]`) and has methods
        ``get()``, ``keys()``, ``values()`` and ``items()``. Abstract
        base class defined in `collections.abc.Mapping`.

    path-like
        A value representing a file system path having the type of
        :class:`str` or any path object from :mod:`pathlib`. This
        library **does not accept** :class:`bytes` objects.

    sequence
        An list-like object which behaves like a :term:`collection`, can
        be accessed with indexer syntax (:pt:`obj[index]`) and
        :func:`reversed`, and has methods ``index()`` and ``count()``.
        Abstract base class defined in `collections.abc.Sequence`.

    mutable set
        An set-like object which behaves like a :term:`collection`,
        defines operators ``|=``, ``|``, ``&=``, ``&``, ``-=``, ``-``,
        ``^=``, and ``^``; all comparison operators; and methods ``add()``,
        ``remove()``, ``discard()``, ``clear()``, ``pop()``, and
        ``isdisjoint()``. Abstract base class defined in
        `collections.abc.MutableSet`.
