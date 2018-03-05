# -*- coding: utf-8 -*-
"""
@author: python273
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2018
"""


class BaseConfig(object):

    __slots__ = ('section_name', '_settings', '_section')

    def __init__(self, section, **kwargs):
        self.section_name = section

        self._settings = self.load(**kwargs)
        self._section = self._settings.setdefault(section, {})

    def __getattr__(self, name):
        return self._section.get(name)

    __getitem__ = __getattr__

    def __setattr__(self, name, value):
        if name in self.__slots__:
            return super(BaseConfig, self).__setattr__(name, value)

        self._section[name] = value

    __setitem__ = __setattr__

    def setdefault(self, k, d=None):
        return self._section.setdefault(k, d)

    def clear_section(self):
        self._section.clear()

    def load(self, **kwargs):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError
