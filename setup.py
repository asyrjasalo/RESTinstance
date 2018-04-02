#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from io import open  # required for Python 2
from os.path import abspath, dirname, join
from setuptools import setup, find_packages


CURDIR = dirname(abspath(__file__))

CLASSIFIERS = '''
Development Status :: 4 - Beta
License :: OSI Approved :: Apache Software License
Operating System :: POSIX
Programming Language :: Python
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Topic :: Software Development :: Testing
Framework :: Robot Framework
Framework :: Robot Framework :: Library
'''.strip().splitlines()
with open(join(CURDIR, 'src', 'REST', 'version.py'), encoding="utf-8") as f:
    VERSION = re.search("__version__ = '(.*)'", f.read()).group(1)
with open(join(CURDIR, 'README.rst'), encoding="utf-8") as f:
    DESCRIPTION = f.read()
with open(join(CURDIR, 'requirements.txt'), encoding="utf-8") as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name             = 'RESTinstance',
    version          = VERSION,
    description      = 'Robot Framework test library for (RESTful) JSON APIs',
    long_description = DESCRIPTION,
    author           = 'Anssi Syrjäsalo',
    author_email     = 'anssi.syrjasalo@gmail.com',
    url              = 'https://github.com/asyrjasalo/RESTinstance',
    license          = 'Apache License 2.0',
    keywords         = 'robotframework test library testing rest http json api',
    classifiers      = CLASSIFIERS,
    install_requires = REQUIREMENTS,
    package_dir      = {'': 'src'},
    packages         = find_packages('src')
)
