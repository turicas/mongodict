# coding: utf-8

from setuptools import setup


setup(name='mongodict',
      version='0.1.0',
      author=u'Álvaro Justen',
      author_email='alvarojusten@gmail.com',
      url='https://github.com/turicas/mongodict/',
      description='MongoDB-backed Python dict-like interface',
      zip_safe=True,
      py_modules=['mongodict'],
      install_requires=['pymongo'],
      test_suite='nose.collector',
      license='GPL3',
      keywords=['key-value', 'database', 'mongodb', 'dictionary'],
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
)
