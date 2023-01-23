# -*- coding: utf-8 -*-

# RESTinstance (https://github.com/asyrjasalo/RESTinstance)
# Robot Framework library for RESTful JSON APIs.
#
# Copyright(C) 2018- Anssi Syrjäsalo (http://a.syrjasalo.com)
# Licensed under GNU Lesser General Public License v3 (LGPL-3.0).

import sys

IS_PYTHON_2 = sys.version_info < (3,)

if IS_PYTHON_2:
    STRING_TYPES = (unicode, str)
else:
    STRING_TYPES = str
