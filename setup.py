# coding: utf-8

import sys
from distutils.core import setup


if sys.version_info[0] == 3:
    author_name = 'Álvaro Justen'
else:
    author_name = 'Álvaro Justen'.decode('utf-8')

setup(name='mongodict',
      version='0.3.1',
      author=author_name,
      author_email='alvarojusten@gmail.com',
      url='https://github.com/turicas/mongodict/',
      description='MongoDB-backed Python dict-like interface',
      py_modules=['mongodict'],
      install_requires=['pymongo'],
      license='GPL3',
      keywords=['key-value', 'database', 'mongodb', 'dictionary'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.2',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
)
