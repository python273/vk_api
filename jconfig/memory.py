# -*- coding: utf-8 -*-
"""
:authors: python273
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2019 python273
"""

from .base import BaseConfig


class MemoryConfig(BaseConfig):
    """ Класс конфигурации в памяти

    :param settings: существующий dict с конфигом
    """

    __slots__ = tuple()

    def load(self, settings=None, **kwargs):
        return {} if settings is None else settings

    def save(self):
        pass
