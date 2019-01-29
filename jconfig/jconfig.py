# -*- coding: utf-8 -*-
"""
:authors: python273
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2019 python273
"""


import json

from .base import BaseConfig


class Config(BaseConfig):
    """ Класс конфигурации в файле

    :param filename: имя файла
    """

    __slots__ = ('_filename',)

    def __init__(self, section, filename='.jconfig'):
        self._filename = filename

        super(Config, self).__init__(section, filename=filename)

    def load(self, filename, **kwargs):
        try:
            with open(filename, 'r') as f:
                settings = json.load(f)
        except (IOError, ValueError):
            settings = {}

        settings.setdefault(self.section_name, {})

        return settings

    def save(self):
        with open(self._filename, 'w') as f:
            json.dump(self._settings, f, indent=2, sort_keys=True)
