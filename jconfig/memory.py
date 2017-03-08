# -*- coding: utf-8 -*-
"""
@author: python273
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2017
"""


class MemoryConfig(object):

    __slots__ = ('_section', '_settings')

    def __init__(self, section, filename=None, settings=None):
        self._section = section

        if settings is not None:
            self._settings = settings
        else:
            self._settings = {}

        self._settings.setdefault(section, {})

    def __getattr__(self, name):
        return self._settings[self._section].get(name)

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return super(MemoryConfig, self).__setattr__(name, value)

        self._settings[self._section][name] = value

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def clear_section(self):
        self._settings[self._section] = {}

    def save(self):
        pass
