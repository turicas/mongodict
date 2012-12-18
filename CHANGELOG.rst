Change Log
==========

Version 0.2.1
-------------

### Bugs
- Fix utf8 encoding problem when using `bson.Binary` (#11)
- Fix 16MB-limit problem when calling `MongoDict.keys` (#10)
- `MongoDict.clear()` do not remove collection indexes anymore

### Enhancements
- Raise *instance* of `KeyError` instead of class
- Add `auth` parameter to `MongoDict` (#8)
- Add information about tox in README
- Fixes setup.py to work with python 2.6
- Use `collection.count()` instead of `cursor.count()`


Version 0.2.0
-------------

- Add Python 3.2 support (thanks, @jucacrispim)
- Optimize all queries to hit only the index
- Add docstrings to entire module
- Add ``mongodict.__all__``
- Add ``MongoDict.__del__``
- Use tox to run tests


Version 0.1.1
-------------

- Set ``safe=True`` by default (slower)
- Did some optimizations on ``__getitem__`` and  ``__delitem__``
- Added method ``clear``, an optimized way to delete all keys
- An ``UnicodeDecodeError`` is raised if one of the strings
  (key or value) is not ``unicode`` or ``str`` encoded with ``utf-8`` codec
- Replaced ``insert`` with ``update`` - it was generating an exception when
  updating (already existent) keys
- Add benchmark (Python dict vs Redis vs mongodict)


Version 0.1.0
-------------

- First version released
- Basic ``dict``-like behaviour
