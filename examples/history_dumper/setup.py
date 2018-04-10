# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name = 'history_dumper',
    packages = ['history_dumper'],
    install_requires=['psycopg2', 'vk_api'],
    version = '0.0.1.dev0',
    description = 'history dumper for vk',
    author = 'Kord J.',
    author_email = 'xxkord@gmail.com',
    url = 'https://github.com/xkord/vk_api',
    download_url = 'hhttps://github.com/xkord/vk_api',
    keywords = ['vk', 'vk api', 'pool', 'async', 'history'],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 1 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'
    ],
    entry_points = {
        'console_scripts': ['history_dumper = history_dumper:main'],
    },
    test_suite='history_dumper.tests',
    long_description = '''\

README.md
------------------
'''
)
