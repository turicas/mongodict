# coding: utf-8

from setuptools import setup, find_packages


setup(name='mongodict',
      version='0.1.0-d',
      author=u'Álvaro Justen <alvarojusten@gmail.com>'
      url='https://github.com/turicas/mongodict',
      description='MongoDB-backed Python dict-like interface',
      zip_safe=True,
      packages=find_packages(),
      install_requires=['pymongo'],
      test_suite='nose.collector',
      license='GPL3',
)
