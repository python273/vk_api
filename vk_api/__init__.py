# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2015
"""

__author__ = 'Kirill Python'
__version__ = '6.1'
__email__ = 'python273@ya.ru'
__contact__ = 'https://vk.com/python273'

import sys

if sys.version_info[0] == 2:
    from vk_api import *
    from vk_upload import *
    from vk_tools import *
else:
    from .vk_api import *
    from .vk_upload import *
    from .vk_tools import *
