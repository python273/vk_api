# -*- coding: utf-8 -*-
"""
@author: python273
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2017
"""

import json


class Config(object):
    __slots__ = ('_section', '_filename', '_settings')

    def __init__(self, section, filename='.jconfig'):
        self._section = section
        self._filename = filename
        self._settings = self.load()

    def __getattr__(self, name):
        return self._settings[self._section].get(name)

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super(Config, self).__setattr__(name, value)
            return

        self._settings[self._section][name] = value

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def clear_section(self):
        self._settings[self._section] = {}

    def load(self):
        try:
            with open(self._filename, 'r') as f:
                settings = json.load(f)
        except (IOError, ValueError):
            settings = {}

        settings.setdefault(self._section, {})

        return settings

    def save(self):
        with open(self._filename, 'w') as f:
            json.dump(self._settings, f)
