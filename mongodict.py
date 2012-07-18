# coding: utf-8

from collections import MutableMapping
import pymongo


__version__ = (0, 1, 1)

class MongoDict(MutableMapping):
    def __init__(self, host='localhost', port=27017, database='mongodict',
                 collection='main', default=None, safe=True):
        super(MongoDict, self).__init__()
        self._connection = pymongo.Connection(host=host, port=port, safe=safe)
        self._db = self._connection[database]
        self._collection = self._db[collection]
        self._collection.ensure_index([('_id', 1), ('value', 1)])
        if default is not None:
            self.update(default)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            key = key.decode('utf-8')
        if isinstance(value, str):
            value = value.decode('utf-8')
        return self._collection.update({'_id': key},
                                       {'_id': key, 'value': value},
                                       upsert=True)

    def __getitem__(self, key):
        if isinstance(key, str):
            key = key.decode('utf-8')
        result = self._collection.find_one({'_id': key})
        if not result:
            raise KeyError
        return result['value']

    def __delitem__(self, key):
        if key not in self:
            raise KeyError
        return self._collection.remove({'_id': key})

    def clear(self):
        self._collection.drop()

    def __len__(self):
        return self._collection.find().count()

    def __iter__(self):
        results = self._collection.find({}, {'_id': 1})
        for result in results:
            yield result['_id']

    def __contains__(self, key):
        results = self._collection.find({'_id': key})
        return results.count() > 0
