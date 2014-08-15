# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: http://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2014
"""

__author__ = 'Kirill Python'
<<<<<<< HEAD
__version__ = '4.7.6'
=======
__version__ = '5.0.0'
>>>>>>> refs/remotes/origin/dev
__email__ = 'siberianpython@gmail.com'
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
