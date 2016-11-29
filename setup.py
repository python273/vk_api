#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Kirill Python
@contact: http://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2016
'''

from distutils.core import setup


setup(
    name='vk_api',
    version='8.0',
    author='Kirill Python',
    author_email='whoami@python273.pw',
    url='https://github.com/python273/vk_api',
    description='Module for writing scripts for vk.com (vkontakte)',
    download_url='https://github.com/python273/vk_api/archive/master.zip',
    license='Apache License, Version 2.0, see LICENSE file',

    packages=['vk_api', 'jconfig'],
    install_requires=['requests'],
)
