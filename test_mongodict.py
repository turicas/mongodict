# coding: utf-8

import unittest
import sys
from collections import MutableMapping
import pymongo
from mongodict import MongoDict


class TestMongoDict(unittest.TestCase):
    def setUp(self):
        self.config = {'host': 'localhost', 'port': 27017,
                       'database': 'mongodict', 'collection': 'main'}
        self.connection = pymongo.Connection(host=self.config['host'],
                port=self.config['port'], safe=True)
        self.db = self.connection[self.config['database']]
        self.collection = self.db[self.config['collection']]

    def tearDown(self):
        self.connection.drop_database(self.db)

    def test_should_be_a_MutableMapping(self):
        my_dict = MongoDict()
        self.assertTrue(isinstance(my_dict, MutableMapping))
        expected_methods = ['setitem', 'getitem', 'delitem', 'iter', 'len']
        actual_methods = dir(my_dict)
        for method in expected_methods:
            self.assertIn('__{}__'.format(method), actual_methods)

    def test_set_item(self):
        my_dict = MongoDict(**self.config)
        my_dict['python'] = 'rules'
        results = list(self.collection.find())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['_id'], 'python')
        self.assertEqual(results[0]['value'], 'rules')

    def test_default_items(self):
        my_dict = MongoDict(default={'answer': 42, 'spam': 'ham'},
                            **self.config)
        results = list(self.collection.find())
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['_id'], 'answer')
        self.assertEqual(results[0]['value'], 42)
        self.assertEqual(results[1]['_id'], 'spam')
        self.assertEqual(results[1]['value'], 'ham')

    def test_get_item(self):
        self.collection.insert({'_id': 'testing', 'value': 123})
        self.collection.insert({'_id': 'bla bla bla', 'value': 3.14})
        my_dict = MongoDict(**self.config)
        self.assertEqual(my_dict['testing'], 123)
        self.assertEqual(my_dict['bla bla bla'], 3.14)
        with self.assertRaises(KeyError):
            temp = my_dict['non ecxiste']

    def test_del_item(self):
        self.collection.insert({'_id': 'testing', 'value': 123})
        self.collection.insert({'_id': 'bla bla bla', 'value': 3.14})
        my_dict = MongoDict(**self.config)
        del my_dict['testing']
        results = list(self.collection.find())
        self.assertEqual(results, [{'_id': 'bla bla bla', 'value': 3.14}])
        with self.assertRaises(KeyError):
            del my_dict['non ecxiste']

    def test_len(self):
        for counter in range(1000):
            self.collection.insert({'_id': 'test-' + str(counter),
                                    'value': counter})
        my_dict = MongoDict(**self.config)
        self.assertEqual(self.collection.find().count(), len(my_dict))

    def test_iter(self):
        for counter in range(10):
            self.collection.insert({'_id': 'test-' + str(counter),
                                    'value': counter})
        my_dict = MongoDict(**self.config)
        keys = []
        for key in my_dict:
            keys.append(key)
        self.assertEqual(len(keys), 10)
        expected_keys = ['test-' + str(counter) for counter in range(10)]
        self.assertEqual(set(keys), set(expected_keys))
        self.assertEqual(set(my_dict.keys()), set(expected_keys))
        my_dict['python'] = 10
        expected_keys.append('python')
        self.assertEqual(set(my_dict.keys()), set(expected_keys))

        results = []
        for key, value in my_dict.items():
            results.append((key, value))
        values = [x[1] for x in results]
        expected_values = list(range(11))
        self.assertEqual(set(values), set(expected_values))
        self.assertEqual(set(my_dict.values()), set(expected_values))

    def test_in(self):
        self.collection.insert({'_id': 'testing', 'value': 123})
        my_dict = MongoDict(**self.config)
        self.assertIn('testing', my_dict)
        self.assertNotIn('python', my_dict)

    def test_clear(self):
        for counter in range(10):
            self.collection.insert({'_id': 'test-' + str(counter),
                                    'value': counter})
        my_dict = MongoDict(**self.config)
        index_count_before = len(self.collection.index_information())
        my_dict.clear()
        index_count_after = len(self.collection.index_information())
        self.assertEqual(self.collection.find().count(), 0)

        # MongoDict.clear() should not delete indexes
        self.assertEqual(index_count_before, index_count_after)

    def test_should_be_possible_to_assign_new_values_to_existing_keys(self):
        my_dict = MongoDict(**self.config)
        my_dict['python'] = 'rules'
        my_dict['python'] = 42
        self.assertNotEqual(my_dict['python'], 'rules')
        self.assertEqual(my_dict['python'], 42)


    def test_non_unicode_strings(self):
        my_dict = MongoDict(**self.config)
        if sys.version < '3':
            string_1 = unicode('Álvaro Justen'.decode('utf-8'))\
                .encode('iso-8859-15')
        else:
            string_1 = 'Álvaro Justen'.encode('iso-8859-15')

        with self.assertRaises(UnicodeError):
            my_dict[string_1] = 123
        with self.assertRaises(UnicodeError):
            temp = my_dict[string_1]
        with self.assertRaises(UnicodeError):
            my_dict['python'] = string_1
        with self.assertRaises(UnicodeError):
            string_1 in my_dict
        with self.assertRaises(UnicodeError):
            del my_dict[string_1]

    def test_deletion_of_MongoDict_object(self):
        config = self.config.copy()
        config['safe'] = False
        my_dict = MongoDict(**config)
        for i in range(1000):
            my_dict['testing_' + str(i)] = i
        del my_dict
        self.assertEqual(self.collection.find().count(), 1000)

    def test_keys_method_should_not_raises_exception_if_more_than_16MB(self):
        my_dict = MongoDict(**self.config)
        key_template = ('python' * 100) + '{}'
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
        # do not use assertEqual here! The content is too big

class TestMemcacheAPI(unittest.TestCase):
    def setUp(self):
        self.config = {'host': 'localhost', 'port': 27017,
                       'database': 'mongodict', 'collection': 'main'}
        self.connection = pymongo.Connection(host=self.config['host'],
                port=self.config['port'], safe=True)
        self.db = self.connection[self.config['database']]
        self.collection = self.db[self.config['collection']]
        self.my_dict = MongoDict(**self.config)

    def tearDown(self):
        self.connection.drop_database(self.db)

    def test_set(self):
        self.my_dict.set('spam', 'eggs')
        self.assertEqual(self.my_dict['spam'], 'eggs')

        self.my_dict.set('spam', 'ham')
        self.assertEqual(self.my_dict['spam'], 'ham')

        self.assertEqual(self.my_dict.set('some key', 'some value'), True)

    def test_get(self):
        self.my_dict['python'] = 'rules'
        self.assertEqual(self.my_dict.get('python'), 'rules')

        self.assertEqual(self.my_dict.get('key-that-does-not-exist-1'), None)
        self.assertEqual(self.my_dict.get('key-that-does-not-exist-2', 0), 0)
        self.assertEqual(self.my_dict.get('key-that-does-not-exist-3', -1), -1)

    #TODO: delete - must return True
    #TODO: incr - what if it's str?
    #TODO: decr
    #TODO: get_multi, set_multi, delete_multi
    #TODO: more actions?
