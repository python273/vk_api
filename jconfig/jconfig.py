# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: http://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2014
"""

import os
import json


class Config(object):
    def __init__(self, section, filename=None):

        if not filename:
            filename = 'config'

        self.section = section  # Секция настроек
        self.filename = filename  # Файл с настройками
        self.all = self.parse()  # Все настройки
        self.settings = self.all.get(section, {})  # Настройки секции

    def __getitem__(self, item):
        return self.settings.get(item, {})

    def __setitem__(self, key, value):
        self.settings.update({key: value})
        self.all.update({self.section: self.settings})
        self.update(self.all)

    def parse(self):
        fileis = os.path.exists(self.filename)
        if fileis:
            settings = json.load(open(self.filename, 'r'))
            return settings
        else:
            self.update()
            return {}

    def update(self, settings=None):
        if not settings:
            settings = {}

        json.dump(settings, open(self.filename, 'w'))
