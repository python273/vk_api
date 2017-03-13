# -*- coding: utf-8 -*-
"""
@author: python273
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2017
"""

import sys

from .execute import VkFunction


if sys.version_info.major == 2:
    range = xrange


class VkTools(object):
    """ Содержит некоторые воспомогательные функции, которые могут понадобиться
        при использовании API
    """

    __slots__ = ('vk',)

    def __init__(self, vk):
        """
        :param vk: объект VkApi
        """
        self.vk = vk

    def get_all_iter(self, method, max_count, values=None, key='items',
                     limit=None):
        """ Получить все элементы
        Работает в методах, где в ответе есть count и items или users
        За один запрос получает max_count * 25 элементов

        :param method: метод
        :type method: str

        :param values: параметры
        :type values: dict

        :param max_count: максимальное количество элементов,
                            которое можно получить за один раз
        :type max_count: int

        :param key: ключ элементов, которые нужно получить
        :type key: str

        :param limit: ограничение на кол-во получаемых элементов,
                            но может прийти больше
        :type limit: int
        """

        if values:
            values = values.copy()
        else:
            values = {}

        items_count = 0
        offset = 0

        while True:
            response = vk_get_all_items(
                self.vk, method, values, key, max_count, offset
            )

            items = response.get('items')
            offset = response.get('offset')

            if items is None or response.get('count') is None:
                break  # Error

            items_count += len(items)

            for item in items:
                yield item

            if offset >= response['count']:
                break

            if limit and len(items) >= limit:
                break

    def get_all(self, method, max_count, values=None, key='items', limit=None):
        """ Использовать только если нужно загрузить все объекты в память.

            Eсли вы можете обрабатывать объекты по частям, то лучше
            использовать get_all_iter

            Например если вы записываете объекты в БД, то нет смысла загружать
            все данные в память
        """

        items = list(self.get_all_iter(method, max_count, values, key, limit))

        return {'count': len(items), key: items}

    def get_all_slow_iter(self, method, max_count, values=None, key='items',
                          limit=None):
        """ Получить все элементы
        Работает в методах, где в ответе есть count и items или users

        :param method: метод
        :param values: параметры
        :param max_count: максимальное количество элементов,
                            которое можно получить за один раз
        :param key: ключ элементов, которые нужно получить
        :param limit: ограничение на кол-во получаемых элементов,
                            но может прийти больше
        """

        if not values:
            values = {}
        else:
            values = values.copy()

        values.update({'count': max_count})

        response = self.vk.method(method, values)
        count = response['count']
        items_count = 0

        for i in range(max_count, count + 1, max_count):
            values.update({
                'offset': i
            })

            response = self.vk.method(method, values)
            items = response[key]
            items_count += len(items)

            for item in items:
                yield item

            if limit and len(items_count) >= limit:
                break

    def get_all_slow(self, method, max_count, values=None, key='items',
                     limit=None):
        """ Использовать только если нужно загрузить все объекты в память.

            Eсли вы можете обрабатывать объекты по частям, то лучше
            использовать get_all_slow_iter

            Например если вы записываете объекты в БД, то нет смысла загружать
            все данные в память
        """

        items = list(
            self.get_all_slow_iter(method, max_count, values, key, limit)
        )
        return {'count': len(items), key: items}


vk_get_all_items = VkFunction(
    args=('method', 'values', 'key', 'max_count', 'start_offset'),
    clean_args=('method', 'max_count', 'start_offset'),
    code='''
    var max_count = %(max_count)s,
        offset = %(start_offset)s,
        key = %(key)s;

    var params = {count: max_count, offset: offset} + %(values)s;

    var r = API.%(method)s(params),
        items = r[key],
        i = 1;

    while(i < 25 && offset + max_count <= r.count) {
        offset = offset + max_count;
        params.offset = offset;

        items = items + API.%(method)s(params)[key];

        i = i + 1;
    };

    return {count: r.count, items: items, offset: offset + max_count};
''')
