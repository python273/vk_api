#!/usr/bin/env python
""" Setup file for vk_api package """

from distutils.core import setup
setup(name='vk_api',
      version='4.0',
      description='Module to use the API VKontakte',
      author='Kirill Python',
      author_email='mikeking568@gmail.com',
      url='https://github.com/python273/vk_api',
      packages=['vk_api', 'vk_api.upload', 'jconfig'],
     )
