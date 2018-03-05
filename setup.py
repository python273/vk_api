#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

"""
@author: python273
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2018
"""


setup(
    name='vk_api',
    version='9.3.1',
    author='python273',
    author_email='whoami@python273.pw',
    url='https://github.com/python273/vk_api',
    description='Module for writing scripts for vk.com (vkontakte)',
    download_url='https://github.com/python273/vk_api/archive/master.zip',
    license='Apache License, Version 2.0, see LICENSE file',

    packages=['vk_api', 'jconfig'],
    install_requires=['requests', 'enum34'],

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
    ]
)
