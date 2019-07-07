#!/usr/bin/env python
# -*- coding: utf-8 -*-
from io import open
from setuptools import setup

"""
:authors: python273
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2019 python273
"""


version = '11.5.0'

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='vk_api',
    version=version,

    author='python273',
    author_email='vk_api@python273.pw',

    description=(
        u'Python модуль для написания скриптов для социальной сети '
        u'Вконтакте (vk.com) (API wrapper)'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/python273/vk_api',
    download_url='https://github.com/python273/vk_api/archive/v{}.zip'.format(
        version
    ),

    license='Apache License, Version 2.0, see LICENSE file',

    packages=['vk_api', 'jconfig'],
    install_requires=['requests', 'enum34;python_version<"3.4"', 'six'],
    extras_require={
        'vkstreaming': ['websocket-client'],
        'vkaudio': ['beautifulsoup4'],
    },

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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
    ]
)
