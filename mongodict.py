# coding: utf-8

''' MongoDB-backed Python ``dict``-like interface

So you are storing some key-values in a ``dict`` but your data became huge than
your memory or you want to persist it on the disk? Then `mongodict
<https://github.com/turicas/mongodict>`_ is for
you!

As it uses `MongoDB <http://mongodb.org/>`_ to store the data, you get all cool
`MongoDB <http://mongodb.org/>`_ things, like shardings and replicas.

`mongodict <https://github.com/turicas/mongodict>`_ is supported under
`Python 2.7 <http://www.python.org/getit/releases/2.7/>`_ and
`Python 3.2 <http://www.python.org/getit/releases/3.2/>`_.
'''

import sys
from collections import MutableMapping
import pymongo


__version__ = (0, 2, 0)
__all__ = ['MongoDict']

if sys.version_info.major == 3:
    unicode_type = str
    byte_type = bytes
else:
    unicode_type = unicode
    byte_type = str

class MongoDict(MutableMapping):
    ''' ``dict``-like interface for storing data in MongoDB '''

    _index = [('_id', 1), ('value', 1)]

    def __init__(self, host='localhost', port=27017, database='mongodict',
                 collection='main', default=None, safe=True):
        ''' MongoDB-backed Python ``dict``-like interface

        Create a new MongoDB connection '''
        super(MongoDict, self).__init__()
        self._connection = pymongo.Connection(host=host, port=port, safe=safe)
        self._db = self._connection[database]
        self._collection = self._db[collection]
        self._collection.ensure_index(self._index)
        if default is not None:
            self.update(default)

    def __setitem__(self, key, value):
        ''' Insert/update a key (uses upsert)

        ``key`` and ``value`` must be unicode or UTF-8.
        '''
        if isinstance(key, byte_type):
            key = key.decode('utf-8')
        if isinstance(value, byte_type):
            value = value.decode('utf-8')
        return self._collection.update({'_id': key},
                                       {'_id': key, 'value': value},
                                       upsert=True)

    def __getitem__(self, key):
        ''' Return the value for key ``key``

        ``key`` must be unicode or UTF-8.
        If not found, raises ``KeyError``.
        '''
        if isinstance(key, byte_type):
            key = key.decode('utf-8')
        result = self._collection.find({'_id': key}, {'value': 1, '_id': 0})\
                                 .hint(self._index)
        if result.count() == 0:
            raise KeyError
        return result[0]['value']

    def __delitem__(self, key):
        ''' Delete the key/value for key ``key``

        ``key`` must be unicode or UTF-8.
        If not found, raises ``KeyError``.
        '''
        if key not in self:
            raise KeyError
        return self._collection.remove({'_id': key})

    def clear(self):
        ''' Delete all key/value pairs '''
        self._collection.drop()

    def __len__(self):
        ''' Return how many key/value pairs are stored '''
        return self._collection.find().count()

    def __iter__(self):
        ''' Iterate over all stored keys '''
        for result in iter(self._collection.distinct('_id')):
            yield result

    def __contains__(self, key):
        ''' Return True/False if a key is/is not stored in the collection '''
        results = self._collection.find({'_id': key}, {'_id': 1})
        return results.count() > 0

    def __del__(self):
        ''' Sync all operations and disconnect '''
        self._connection.fsync()
        self._connection.disconnect()
