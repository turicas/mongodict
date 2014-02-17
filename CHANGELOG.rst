Change Log
==========

Version 0.3.1
-------------

This version BREAKS DATA COMPATIBILITY with 0.3.0. Please see below:

- Option to specify index type: key-only or key-and-value. If you specify "key
  and value" you can't have documents (key + value) greater than 16MB. Default
  option moved to key-only (fixes `issue #14
  <https://github.com/turicas/mongodict/issues/14>`_);
- Replace ``value`` with ``v`` as the key inside Mongo document to save space.
  Note that you will need to migrate your data! A little script is provided.


Version 0.3.0
-------------

- Added a "codec" concept, so user can customized how value data is saved.
  `Pickle is the default codec <https://github.com/turicas/mongodict/issues/12>`_;
- Added a
  `migration script <https://github.com/turicas/mongodict/blob/master/migrate_data.py>`_
  to migrate data from mongodict <= 0.2.1;
- `Using basic mapping (dict) interface tests from python source
  <https://github.com/turicas/mongodict/issues/13>`_;
- Updated `tox <https://pypi.python.org/pypi/tox>`_ config to use Python 2.7.5
  and Python 3.3.2 to run tests.


Version 0.2.1
-------------

- [Bug] Fix utf8 encoding problem when using ``bson.Binary`` (#11)
- [Bug] Fix 16MB-limit problem when calling ``MongoDict.keys`` (#10)
- [Bug] ``MongoDict.clear()`` do not remove collection indexes anymore
- Raise *instance* of ``KeyError`` instead of class
- Add ``auth`` parameter to ``MongoDict`` (#8)
- Add information about tox in README
- Fixes setup.py to work with python 2.6
- Use ``collection.count()`` instead of ``cursor.count()``


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
