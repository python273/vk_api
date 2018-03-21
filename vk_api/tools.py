# -*- coding: utf-8 -*-
"""
@author: python273
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2018
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
                     limit=None, stop_fn=None, negative_offset=False):
        """ Получить все элементы.
        Работает в методах, где в ответе есть count и items или users.
        За один запрос получает max_count * 25 элементов

        :param method: имя метода
        :type method: str

        :param max_count: максимальное количество элементов, которое можно
                          получить за один запрос
        :type max_count: int

        :param values: параметры
        :type values: dict

        :param key: ключ элементов, которые нужно получить
        :type key: str

        :param limit: ограничение на кол-во получаемых элементов,
                            но может прийти больше
        :type limit: int

        :param stop_fn: функция, отвечающая за выход из цикла
        :type stop_fn: func
        """

        values = values.copy() if values else {}

        values['count'] = max_count
        values['offset'] = 0
        items_count = 0
        count = None
        have_more = True

        while have_more:
            response = vk_get_all_items(
                self.vk, method=method, key=key, values=values, count=count,
                offset_mul=-1 if negative_offset else 1
            )
            count = response['count']

            items = response[key]
            items_count += len(items)

            for item in items:
                yield item

            if limit and items_count >= limit:
                break

            if stop_fn and stop_fn(items):
                break

            values['offset'] = response['offset']
            have_more = response['have_more']

    def get_all(self, method, max_count, values=None, key='items', limit=None,
                stop_fn=None):
        """ Использовать только если нужно загрузить все объекты в память.

            Eсли вы можете обрабатывать объекты по частям, то лучше
            использовать get_all_iter

            Например если вы записываете объекты в БД, то нет смысла загружать
            все данные в память
        """

        items = list(self.get_all_iter(method, max_count, values, key, limit,
                                       stop_fn))

        return {'count': len(items), key: items}

    def get_all_slow_iter(self, method, max_count, values=None, key='items',
                          limit=None, stop_fn=None, negative_offset=False):
        """ Получить все элементы (без использования execute)
        Работает в методах, где в ответе есть count и items или users

        :param method: имя метода
        :type method: str

        :param max_count: максимальное количество элементов, которое можно
                          получить за один запрос
        :type max_count: int

        :param values: параметры
        :type values: dict

        :param key: ключ элементов, которые нужно получить
        :type key: str

        :param limit: ограничение на кол-во получаемых элементов,
                            но может прийти больше
        :type limit: int

        :param stop_fn: функция, отвечающая за выход из цикла
        :type stop_fn: func
        """

        values = values.copy() if values else {}
        values['count'] = max_count
        values['offset'] = 0

        offset_mul = -1 if negative_offset else 1
        items_count = 0
        count = None
        while values['offset'] < (count or 1):
            values['offset'] *= offset_mul
            response = self.vk.method(method, values)
            values['offset'] *= offset_mul
            new_count = response['count']
            count_diff = new_count - (count or new_count)

            if new_count == 0:
                break

            if count_diff < 0:
                values['offset'] += count_diff
                count = new_count
                continue

            items = response[key][count_diff:]
            items_count += len(items)

            for item in items:
                yield item

            if limit and items_count >= limit:
                break

            if stop_fn and stop_fn(items):
                break

            if len(items) < max_count:
                break

            values['offset'] += len(items) + count_diff
            count = new_count

    def get_all_slow(self, method, max_count, values=None, key='items',
                     limit=None, stop_fn=None):
        """ Использовать только если нужно загрузить все объекты в память.

            Eсли вы можете обрабатывать объекты по частям, то лучше
            использовать get_all_slow_iter

            Например если вы записываете объекты в БД, то нет смысла загружать
            все данные в память
        """

        items = list(
            self.get_all_slow_iter(method, max_count, values, key, limit,
                                   stop_fn)
        )
        return {'count': len(items), key: items}


vk_get_all_items = VkFunction(
    args=('method', 'key', 'values', 'count', 'offset_mul'),
    clean_args=('method', 'key', 'offset_mul'),
    code='''
    var params = %(values)s,
        calls = 0,
        items = [],
        count = %(count)s;

    while(calls < 25) {
        calls = calls + 1;
        params.offset = params.offset * %(offset_mul)s;
        var response = API.%(method)s(params), 
            new_count = response.count,
            count_diff = (count == null ? 0 : new_count - count);
        params.offset = params.offset * %(offset_mul)s;
        if (new_count == 0) {
            calls = 99;
        } else if (count_diff < 0) {
            params.offset = params.offset + count_diff;
            count = new_count;
        } else {
            var r_items = response.%(key)s.slice(count_diff);
            if (r_items.length < params.count) {
                calls = 99;
            }
            items = items + r_items;
            params.offset = params.offset + params.count + count_diff;
            count = new_count;
        }
        if (count != null && params.offset >= count) {
            calls = 99;
        }
    };

    return {count: count, items: items, offset: params.offset, have_more: calls != 99};
''')
