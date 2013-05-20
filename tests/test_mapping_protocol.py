# coding: utf-8

import random
import string
import sys

if sys.version_info[0] == 2:
    import mapping_tests_py275 as mapping_tests
else:
    import mapping_tests_py332 as mapping_tests

import pymongo

from mongodict import MongoDict


MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
MONGO_DATABASE = 'mongodict_test'


def random_string(length=32):
    return ''.join([random.choice(string.ascii_lowercase)
                    for i in range(length)])


class TestMappingProtocol(mapping_tests.BasicTestMappingProtocol):
    def setUp(self):
        self._connection = pymongo.Connection(host=MONGO_HOST, port=MONGO_PORT)
        self._db = self._connection[MONGO_DATABASE]
        self.collections = []

    def tearDown(self):
        for collection in self.collections:
            self._db.drop_collection(collection)

    def type2test(self):
        collection_name = random_string()
        self.collections.append(collection_name)
        return MongoDict(host=MONGO_HOST, port=MONGO_PORT,
                         database=MONGO_DATABASE, collection=collection_name)
