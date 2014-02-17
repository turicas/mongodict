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
try:
    import cPickle as pickle
except ImportError:
    import pickle

from collections import MutableMapping

import pymongo

from bson import Binary


__version__ = (0, 3, 1)
__all__ = ['MongoDict']
INDEX_KEY = [('_id', 1)]
INDEX_KEY_VALUE = [('_id', 1), ('v', 1)]

if sys.version_info[0] == 2:
    binary_type = str
else:
    binary_type = bytes

def pickle_dumps(value):
    return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)

class MongoDict(MutableMapping):
    ''' ``dict``-like interface for storing data in MongoDB '''


    def __init__(self, host='localhost', port=27017, database='mongodict',
                 collection='main', codec=(pickle_dumps, pickle.loads),
                 safe=True, auth=None, default=None, index_type='key'):
        ''' MongoDB-backed Python ``dict``-like interface

        Create a new MongoDB connection.
        `auth` must be (login, password)'''
        super(MongoDict, self).__init__()
        self._connection = pymongo.Connection(host=host, port=port, safe=safe)
        self._safe = safe
        self._db = self._connection[database]
        if auth is not None:  # TODO: test auth
            if not self._db.authenticate(*auth):
                raise ValueError('Cannot authenticate to MongoDB server.')
        self._collection = self._db[collection]
        if index_type == 'key':
            self._index = INDEX_KEY
        elif index_type == 'key-value':
            self._index = INDEX_KEY_VALUE
        else:
            raise ValueError(u'Error: unknown `index_type`')
        self._collection.ensure_index(self._index)
        self.encode_value = lambda value: Binary(codec[0](value))
        self.decode_value = lambda value: codec[1](binary_type(value))
        if default is not None:
            self.update(default)

    def __setitem__(self, key, value):
        ''' Insert/update a key (uses upsert)

        ``key`` and ``value`` must be unicode or UTF-8.
        '''
        value = self.encode_value(value)
        return self._collection.update({'_id': key},
                                       {'_id': key, 'v': value},
                                       upsert=True)

    def __getitem__(self, key):
        ''' Return the value for key ``key``

        ``key`` must be unicode or UTF-8.
        If not found, raises ``KeyError``.
        '''
        result = self._collection.find({'_id': key},
                                       {'v': 1, '_id': 0})\
                                 .hint(self._index)
        if result.count() == 0:
            raise KeyError(key)
        return self.decode_value(result[0]['v'])

    def __delitem__(self, key):
        ''' Delete the key/value for key ``key``

        ``key`` must be unicode or UTF-8.
        If not found, raises ``KeyError``.
        '''
        if key not in self:
            raise KeyError(key)
        return self._collection.remove({'_id': key})

    def clear(self):
        ''' Delete all key/value pairs '''
        self._collection.remove({}, safe=self._safe)

    def __len__(self):
        ''' Return how many key/value pairs are stored '''
        return self._collection.count()

    def __iter__(self):
        ''' Iterate over all stored keys '''
        return (pair['_id']
                for pair in self._collection.find({}, {'_id': 1}))

    def __contains__(self, key):
        ''' Return True/False if a key is/is not stored in the collection '''
        results = self._collection.find({'_id': key}, {'_id': 1})
        return results.count() > 0

    has_key = __contains__

    def __del__(self):
        ''' Sync all operations and disconnect '''
        self._connection.fsync()
        self._connection.disconnect()
