# -*- coding: utf-8 -*-
"""
:authors: python273
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2019 python273
"""


class BaseConfig(object):
    """ Абстрактный базовый класс конфигурации.
    У наследуемых классов должен быть определен `__slots__`

    :param section: имя подкатегории в конфиге
    :param \*\*kwargs: будут переданы в :func:`load`
    """

    __slots__ = ('section_name', '_settings', '_section')

    def __init__(self, section, **kwargs):
        self.section_name = section

        self._settings = self.load(**kwargs)
        self._section = self._settings.setdefault(section, {})

    def __getattr__(self, name):
        return self._section.get(name)

    __getitem__ = __getattr__

    def __setattr__(self, name, value):
        try:
            super(BaseConfig, self).__setattr__(name, value)
        except AttributeError:
            self._section[name] = value

    __setitem__ = __setattr__

    def setdefault(self, k, d=None):
        return self._section.setdefault(k, d)

    def clear_section(self):
        self._section.clear()

    def load(self, **kwargs):
        """Абстрактный метод, должен возвращать dict с конфигом"""
        raise NotImplementedError

    def save(self):
        """Абстрактный метод, должен сохранять конфиг"""
        raise NotImplementedError
