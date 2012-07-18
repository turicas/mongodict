# coding: utf-8

from collections import MutableMapping
import pymongo


class MongoDict(MutableMapping):
    def __init__(self, host='localhost', port=27017, database='mongodict',
                 collection='main', default=None):
        super(MongoDict, self).__init__()
        self._connection = pymongo.Connection(host=host, port=port, safe=True)
        self._db = self._connection[database]
        self._collection = self._db[collection]
        if default is not None:
            self.update(default)

    def __setitem__(self, key, value):
        return self._collection.insert({'_id': key, 'value': value})

    def __getitem__(self, key):
        results = self._collection.find({'_id': key})
        if results.count() == 0:
            raise KeyError
        return results[0]['value']

    def __delitem__(self, key):
        if key not in self:
            raise KeyError
        return self._collection.remove({'_id': key})

    def __len__(self):
        return self._collection.find().count()

    def __iter__(self):
        results = self._collection.find({}, {'_id': 1})
        for result in results:
            yield result['_id']

    def __contains__(self, key):
        results = self._collection.find({'_id': key})
        return results.count() > 0
