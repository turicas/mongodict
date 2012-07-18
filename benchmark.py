# coding: utf-8

import timeit


test_code = '''
import random
import hashlib
import redis
from mongodict import MongoDict


data = {}
for counter in range(int(random.random() * 10000)):
    my_hash = hashlib.sha512(str(counter)).hexdigest()
    key = 'key-{}-{}'.format(str(counter), my_hash)
    value = hashlib.sha512(key).hexdigest()
    data[key] = value

def test_redis():
    redis_dict = redis.StrictRedis(host='localhost', port=6379, db=0)
    for key in redis_dict.keys():
        redis_dict.delete(key)
    for key, value in data.iteritems():
        redis_dict.set(key, value)
        assert redis_dict.get(key) == value

def test_mongodict(safe=True):
    mongo_dict = MongoDict(safe=safe)
    mongo_dict.clear()
    for key, value in data.iteritems():
        mongo_dict[key] = value
        assert mongo_dict[key] == value

def test_pythondict():
    python_dict = {}
    python_dict.clear()
    for key, value in data.iteritems():
        python_dict[key] = value
        assert python_dict[key] == value
'''

def main():
    iterations = 10
    tests = {'Python dict': 'test_pythondict()',
             'Redis': 'test_redis()',
             'MongoDict(safe=False)': 'test_mongodict(safe=False)',
             'MongoDict(safe=True)': 'test_mongodict(safe=True)',
    }
    for test_name, function_call in tests.iteritems():
        print test_name, timeit.timeit(function_call, test_code,
                                       number=iterations)
    #TODO: test for other number and sizes of keys/values

if __name__ == '__main__':
    main()
