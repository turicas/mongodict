#!/usr/bin/env python
# coding: utf-8

'''
This script does data migration of data from mongodict <= 0.2.1 to 0.3.0 and
from 0.3.0 to 0.3.1.
The first migration is needed since the new version uses another codec by
default (pickle instead of JSON/BSON) and the later one because the key name
changes on document (`value` to `v`).
'''

import datetime
import sys
import time

import mongodict
import pymongo


encode_nothing = lambda x: x
decode_nothing = lambda x: x
report_template = ('\r{:010d} keys / {:010d} ({:6.2f}%) migrated. '
                   'Duration: {}, ETA: {}')
REPORT_INTERVAL = 10 # in number of keys


def print_report(counter, total, start_time):
    percentual = 100 * (counter / float(total))
    duration = datetime.timedelta((time.time() - start_time) / (24 * 3600))
    duration = str(duration).split('.')[0]
    rate = counter / (time.time() - start_time)
    eta = datetime.timedelta(((total - counter) / rate) / (24 * 3600))
    eta = str(eta).split('.')[0]
    report = report_template.format(counter, total, percentual,
                                    duration, eta)
    sys.stdout.write(report)
    sys.stdout.flush()


def migrate_codec(config_old, config_new):
    '''Migrate data from mongodict <= 0.2.1 to 0.3.0
    `config_old` and `config_new` should be dictionaries with the keys
    regarding to MongoDB server:
        - `host`
        - `port`
        - `database`
        - `collection`
    '''
    assert mongodict.__version__ in [(0, 3, 0), (0, 3, 1)]

    connection = pymongo.Connection(host=config_old['host'],
                                    port=config_old['port'])
    database = connection[config_old['database']]
    collection = database[config_old['collection']]
    new_dict = mongodict.MongoDict(**config_new) # uses pickle codec by default
    total_pairs = collection.count()
    start_time = time.time()
    for counter, pair in enumerate(collection.find(), start=1):
        key, value = pair['_id'], pair['value']
        new_dict[key] = value
        if counter % REPORT_INTERVAL == 0:
            print_report(counter, total_pairs, start_time)
    print_report(counter, total_pairs, start_time)
    print('')

def migrate_key(config_old, config_new):
    '''Migrate data from mongodict == 0.3.0 to 0.3.1
    `config_old` and `config_new` should be dictionaries with the keys
    regarding to MongoDB server:
        - `host`
        - `port`
        - `database`
        - `collection`
    '''
    assert mongodict.__version__ == (0, 3, 1)

    connection = pymongo.Connection(host=config_old['host'],
                                    port=config_old['port'])
    database = connection[config_old['database']]
    collection = database[config_old['collection']]
    new_dict = mongodict.MongoDict(**config_new) # uses `v` as default key
    total_pairs = collection.count()
    start_time = time.time()
    for counter, pair in enumerate(collection.find(), start=1):
        key, value = pair['_id'], new_dict.decode_value(pair['value'])
        new_dict[key] = value
        if counter % REPORT_INTERVAL == 0:
            print_report(counter, total_pairs, start_time)
    print_report(counter, total_pairs, start_time)
    print('')


def parse_mongo_data(data_as_string):
    info = data_as_string.split(':')
    port, database, collection = info[1].split('/')
    return {'host': info[0], 'port': int(port), 'database': database,
            'collection': collection}


def main():
    if mongodict.__version__[1] <= 2:
        sys.stderr.write('You need mongodict >= 0.3.0 to run this script.\n')
        exit(1)

    if len(sys.argv) < 4:
        error_message = ('ERROR: usage: {} <old host:port/db/coll> '
                         '<new host:port/db/coll> <codec|key>\n').format(sys.argv[0])
        sys.stderr.write(error_message)
        exit(2)

    try:
        old_config = parse_mongo_data(sys.argv[1])
        new_config = parse_mongo_data(sys.argv[2])
    except IndexError:
        sys.stderr.write('Error parsing MongoDB server data. Please check.\n')
        exit(3)
    migration_type = sys.argv[3]
    if migration_type not in ('codec', 'key'):
        sys.stderr.write('Invalid migration type: {}'.format(migration_type))
        exit(4)

    print('Starting migration...')
    if migration_type == 'codec':
        migrate_codec(old_config, new_config)
    elif migration_type == 'key':
        migrate_key(old_config, new_config)


if __name__ == '__main__':
    main()
