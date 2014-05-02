# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: http://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2014
"""

__author__ = 'Kirill Python'
__version__ = '1.2'
__email__ = 'siberianpython@gmail.com'
__contact__ = 'https://vk.com/python273'


import sys
if sys.version_info[0] == 2:
    from jconfig import *
else:
    from .jconfig import *
