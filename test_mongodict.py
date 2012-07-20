# coding: utf-8

import unittest
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
        self.assertEquals(len(results), 1)
        self.assertEquals(results[0]['_id'], 'python')
        self.assertEquals(results[0]['value'], 'rules')

    def test_default_items(self):
        my_dict = MongoDict(default={'answer': 42, 'spam': 'ham'},
                            **self.config)
        results = list(self.collection.find())
        self.assertEquals(len(results), 2)
        self.assertEquals(results[0]['_id'], 'answer')
        self.assertEquals(results[0]['value'], 42)
        self.assertEquals(results[1]['_id'], 'spam')
        self.assertEquals(results[1]['value'], 'ham')

    def test_get_item(self):
        self.collection.insert({'_id': 'testing', 'value': 123})
        self.collection.insert({'_id': 'bla bla bla', 'value': 3.14})
        my_dict = MongoDict(**self.config)
        self.assertEquals(my_dict['testing'], 123)
        self.assertEquals(my_dict['bla bla bla'], 3.14)
        with self.assertRaises(KeyError):
            temp = my_dict['non ecxiste']

    def test_del_item(self):
        self.collection.insert({'_id': 'testing', 'value': 123})
        self.collection.insert({'_id': 'bla bla bla', 'value': 3.14})
        my_dict = MongoDict(**self.config)
        del my_dict['testing']
        results = list(self.collection.find())
        self.assertEquals(results, [{'_id': 'bla bla bla', 'value': 3.14}])
        with self.assertRaises(KeyError):
            del my_dict['non ecxiste']

    def test_len(self):
        for counter in range(1000):
            self.collection.insert({'_id': 'test-' + str(counter),
                                    'value': counter})
        my_dict = MongoDict(**self.config)
        self.assertEquals(self.collection.find().count(), len(my_dict))

    def test_iter(self):
        for counter in range(10):
            self.collection.insert({'_id': 'test-' + str(counter),
                                    'value': counter})
        my_dict = MongoDict(**self.config)
        keys = []
        for key in my_dict:
            keys.append(key)
        self.assertEquals(len(keys), 10)
        expected_keys = ['test-' + str(counter) for counter in range(10)]
        self.assertEquals(set(keys), set(expected_keys))
        self.assertEquals(set(my_dict.keys()), set(expected_keys))
        results = []
        for key, value in my_dict.iteritems():
            results.append((key, value))
        values = [x[1] for x in results]
        expected_values = list(range(10))
        self.assertEquals(set(values), set(expected_values))
        self.assertEquals(set(my_dict.values()), set(expected_values))

    def test_in(self):
        self.collection.insert({'_id': 'testing', 'value': 123})
        my_dict = MongoDict(**self.config)
        self.assertIn('testing', my_dict)
        self.assertNotIn('python', my_dict)

    def test_clear(self):
        for counter in range(10):
            self.collection.insert({'_id': 'test-' + str(counter),
                                    'value': counter})
        my_dict = MongoDict()
        my_dict.clear() # should use collections' drop method
        #TODO: test `clear`'s call duration
        self.assertEquals(self.collection.find().count(), 0)

    def test_should_be_possible_to_assign_new_values_to_existing_keys(self):
        my_dict = MongoDict()
        my_dict['python'] = 'rules'
        my_dict['python'] = 42
        self.assertNotEquals(my_dict['python'], 'rules')
        self.assertEquals(my_dict['python'], 42)


    def test_non_unicode_strings(self):
        my_dict = MongoDict()
        string_1 = u'Álvaro Justen'.encode('iso-8859-15')
        with self.assertRaises(UnicodeError):
            my_dict[string_1] = 123
        with self.assertRaises(UnicodeError):
            temp = my_dict[string_1]
        with self.assertRaises(UnicodeError):
            my_dict['python'] = string_1

    #TODO: test other (pickable) objects
