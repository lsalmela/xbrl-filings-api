Documentation conventions
=========================

The library uses NumPy style docstrings. Parameter names are, however,
enclosed in double backticks (````param````) instead of single ones
(```param```) due to Sphinx default domain being ``any``. Single
backticks would lead to errors in resolving the reference.

Each name in the API such as class or function is cross-referenced with
a link only once within the same second level section (sections with
hyphen underline). Later mentions are simple
````inline literals````.

XHTML is written with a capital 'X' as spelled in the
`original XHTML 1.0 specification <https://www.w3.org/TR/xhtml1/>`_.
Were the first letter in lower case, the unfortunate standard would have
more than three capital letters nevertheless.

The special constants :pt:`None`, :pt:`True` and :pt:`False` are used
with role ``pt`` to signify inline Python code formatting. E.g.
``:pt:`None```.

Single quotes are used everywhere in the library except for non-code
literal strings in docstrings and log messages. Python names such as
parameter names are surrounded by single quotes in log messages and
double backquotes in docstrings.

Public superclass members always cross-reference their own class name in
the short summaries of docstrings. This ensures subclasses have required
links in their autosummaries.

Colon is not used in attribute docstring short summaries (e.g.
``JSON:API``) as :mod:`~sphinx.ext.napoleon` considers it to separate
attribute type from description. Write JSON:API as JSON-API instead.

Documented class members (public and certain special methods, see
``autodoc_default_options['special-members']`` value in ``conf.py``) are
ordered according to :func:`order_columns` order if they are subclasses
of `APIResource`, otherwise alphabetically. Special methods are always
ordered after public methods.

Order methods in groups and prefer alphabetic ordering (custom order if
seems awkward, especially regarding dataclasses). Groups should be in
the following order:

1. Static methods
2. Class methods
3. ``__init__()`` method
4. Properties
5. Other ``__dunder__()`` methods
6. Private methods
7. Large quantities of related methods on a specific area (e.g.
   superclass overrides)

All external URLs in narrative documentation are placed in the start of
the RST document before top section heading. This is due to easier
maintenance as URLs sometimes break. The first rows should be written in
the following fashion:

.. code-block:: restructuredtext

    .. _linked words in the document: https://www.example.com

And the link in the paragraphs should be created this way:

.. code-block:: restructuredtext

    A paragraph which contains the `linked words in the document`_.

Definition of private
---------------------

The private prefix (underscore) is used in the scope of the object to
define members which should not be accessed outside of the object. The
scope of this rule begins from module members.

Consequently, an underscore-prefixed class is internal to the module, a
prefixed attribute is internal to the class etc.
