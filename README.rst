mongodict - MongoDB-backed Python dict-like interface
=====================================================

So you are storing some key-values in a ``dict`` but your data became huge than
your memory or you want to persist it on the disk? Then `mongodict
<https://github.com/turicas/mongodict>`_ is for
you!

As it uses `MongoDB <http://mongodb.org/>`_ to store the data, you get all cool
`MongoDB <http://mongodb.org/>`_ things, like shardings and replicas.


Installation
------------

As simple as::

    pip install mongodict

or::

    easy_install mongodict


Usage
-----

As it uses
`collections.MutableMapping <http://docs.python.org/library/collections.html#collections.MutableMapping>`_
as its base, you just need to change the line which creates your ``dict``.
For instace, just replace::

    >>> my_dict = {}

with::

    >>> from mongodict import MongoDict
    >>> my_dict = MongoDict(host='localhost', port=27017, database='my_dict',
                            collection='store')

and then use it like a normal ``dict``::

    >>> my_dict['python'] = 'rules'
    >>> print my_dict['python']
    'rules'
    >>> del my_dict['python']
    >>> print my_dict['python']
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "mongodict.py", line 23, in __getitem__
        raise KeyError
    KeyError

Enjoy! :-)

.. NOTE::
   There is no kind of in-memory cache, so all key lookups will be translated
   in a `MongoDB <http://mongodb.org/>`_ query but as
   `MongoDB <http://mongodb.org/>`_'s server put everything it can in memory,
   probably it'll not be a problem (if your working set is always entire in
   memory).


Why not Redis?
--------------

`Redis <http://redis.io/>`_ is "remote directory server" - it's a great piece
of software and can do the job if all your data fit on memory. By other side,
`MongoDB <http://mongodb.org/>`_ already have mature sharding and replica set
features. So, if you need to store lots of key-value pairs that don't fit on
memory, `mongodict <https://github.com/turicas/mongodict>`_ can solve your
problem.

.. NOTE::
   `mongodict <https://github.com/turicas/mongodict>`_ does not have the same
   API other key-value software have
   (like `memcached <http://memcached.org/>`_). Some features are missing to
   compete directly with these kind of software (by now we have only the
   ``dict``-like behaviour), but I have plans to add it soon.


Author
------

This software was written and is maintained by
`Álvaro Justen (aka Turicas) <https://github.com/turicas>`_.
Please contact me at ``alvarojusten`` *at* ``gmail`` *dot* ``com``.


Semantic Versioning
-------------------

This software uses `Semantic Versioning <http://semver.org/>`_.


License
-------

It's licensed under `GPL version 3 <https://www.gnu.org/licenses/gpl-3.0.html>`_.
