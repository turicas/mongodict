# coding: utf-8

import json
import pickle
import sys
import unittest

from collections import MutableMapping

import pymongo

from bson import Binary
from mongodict import MongoDict


if sys.version_info[0] < 3: # Python 2
    binary_type = str
    key_1 = 'Álvaro'.decode('utf-8')
    key_2 = 'Álvaro'
else:
    binary_type = bytes
    key_1 = 'Álvaro'
    key_2 = 'Álvaro'.encode('utf-8')


def encode(value):
    return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)


def decode(value):
    return pickle.loads(value)


class TestMongoDict(unittest.TestCase):
    def setUp(self):
        self.config = {'host': 'localhost', 'port': 27017,
                       'database': 'mongodict', 'collection': 'main',}
        # as no codec is specified, it uses the default (pickle)
        self.connection = pymongo.Connection(host=self.config['host'],
                port=self.config['port'], safe=True)
        self.db = self.connection[self.config['database']]
        self.collection = self.db[self.config['collection']]

    def tearDown(self):
        self.connection.drop_database(self.db)

    def test_set_item_should_save_data_in_collection(self):
        my_dict = MongoDict(**self.config)
        my_dict['python'] = 'rules'
        results = list(self.collection.find())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['_id'], 'python')
        self.assertEqual(decode(results[0]['value']), 'rules')

    def test_get_item_should_retrieve_data_from_collection(self):
        self.collection.insert({'_id': 'testing',
                                'value': Binary(encode('123'))})
        self.collection.insert({'_id': 'bla bla bla',
                                'value': Binary(encode('3.14'))})
        my_dict = MongoDict(**self.config)
        self.assertEqual(my_dict['testing'], '123')
        self.assertEqual(my_dict['bla bla bla'], '3.14')
        with self.assertRaises(KeyError):
            temp = my_dict['non ecxiste']

    def test_del_item_should_delete_pair_in_the_collection(self):
        self.collection.insert({'_id': 'testing',
                                'value': Binary(encode('123'))})
        self.collection.insert({'_id': 'bla bla bla',
                                'value': Binary(encode('3.14'))})
        my_dict = MongoDict(**self.config)
        del my_dict['testing']
        results = list(self.collection.find())
        self.assertEqual(results[0]['_id'], 'bla bla bla')
        self.assertEqual(decode(results[0]['value']), '3.14')
        with self.assertRaises(KeyError):
            del my_dict['non ecxiste']

    def test_should_be_possible_to_assign_new_values_to_existing_keys(self):
        my_dict = MongoDict(**self.config)
        my_dict['python'] = 'rules'
        my_dict['python'] = '42'
        self.assertNotEqual(my_dict['python'], 'rules')
        self.assertEqual(my_dict['python'], '42')

    def test_deletion_of_MongoDict_object_should_sync_data_even_without_safe(self):
        config = self.config.copy()
        config['safe'] = False
        my_dict = MongoDict(**config)
        for i in range(1000):
            my_dict['testing_' + str(i)] = str(i)
        del my_dict
        self.assertEqual(self.collection.find().count(), 1000)

    def test_keys_method_should_not_raises_exception_if_more_than_16MB(self):
        '''Should not raise exception if sum of keys is greater 16MB

        Bug reported by @andrebco:
            <https://github.com/turicas/mongodict/issues/10>
        '''
        my_dict = MongoDict(**self.config)
        key_template = ('python-rules' * 100000) + '{}'
        key_byte_count = 0
        key_count = 0
        keys = set()
        while key_byte_count < 20 * 1024 * 1024: # 20MB > 16MB
            new_key = key_template.format(key_count)
            my_dict[new_key] = 'some value'
            key_byte_count += len(new_key)
            key_count += 1
            keys.add(new_key)
        dict_keys = my_dict.keys()
        self.assertEquals(len(keys), len(dict_keys))
        self.assertTrue(keys == set(dict_keys))
        # do not use assertEqual here because the content is too big and if it
        # fails, stdout will be flooded by irrelevant data

    def test_pickle_codec_should_return_same_objects(self):
        self.collection.drop()
        data = {'first': 12, key_2: [3, 4], key_1: {123: 456}}
        # since key_1 and key_2 has the same information (one is unicode, other
        # is bytes), the contents are overwritten in MongoDict (but not in
        # Python dict, since it recognizes these objects as differents)
        expected = {'first': 12, key_1: {123: 456}}
        self.config['default'] = data
        my_dict = MongoDict(**self.config)
        self.assertEqual(my_dict['first'], 12)
        self.assertIn(my_dict[key_1], ([3, 4], {123: 456}))

    def test_customized_codec(self):
        self.collection.drop()
        self.config['codec'] = (lambda x: json.dumps(x).encode('utf-8'),
                                json.loads)
        data = {'first': (1, 2), 'test': [3, 4], 'test2': {'...': 456}}
        expected = [('first', [1, 2]), ('test', [3, 4]),
                    ('test2', {'...': 456})]
        # JSON represents Python tuples as arrays and deserialized arrays as
        # lists, so our tuples turn lists

        self.config['default'] = data
        my_dict = MongoDict(**self.config)

        for result in self.collection.find():
            key = result['_id']
            value = json.loads(result['value'].decode('utf-8'))
            pair = (key, value)
            self.assertIn(pair, expected)
            expected.remove(pair)
            #we need to remove every pair in this list (instead of just adding
            #it to a dict and then comparing the whole dicts) because JSON
            #encodes tuples as arrays and decodes arrays as lists and we can't
            #have a list as a dict key since it is not hashable
        self.assertEqual(expected, [])

    # TODO: test types of keys (str, unicode)?
