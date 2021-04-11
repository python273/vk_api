# -*- coding: utf-8 -*-
"""
:authors: python273
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2019 python273
"""

from .exceptions import ApiError, VkToolsException
from .execute import VkFunction


class VkTools(object):
    """ Содержит некоторые вспомогательные функции, которые могут понадобиться
    при использовании API

    :param vk: Объект :class:`VkApi`
    """

    __slots__ = ('vk',)

    def __init__(self, vk):
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

        :param limit: ограничение на количество получаемых элементов,
                            но может прийти больше
        :type limit: int

        :param stop_fn: функция, отвечающая за выход из цикла
        :type stop_fn: func

        :param negative_offset: True если offset должен быть отрицательный
        :type negative_offset: bool
        """

        values = values.copy() if values else {}
        values['count'] = max_count

        offset = max_count if negative_offset else 0
        items_count = 0
        count = None

        while True:
            response = vk_get_all_items(
                self.vk, method, key, values, count, offset,
                offset_mul=-1 if negative_offset else 1
            )

            if 'execute_errors' in response:
                raise VkToolsException(
                    'Could not load items: {}'.format(
                        response['execute_errors']
                    ),
                    response=response
                )

            response = response['response']

            items = response["items"]
            items_count += len(items)

            for item in items:
                yield item

            if not response['more']:
                break

            if limit and items_count >= limit:
                break

            if stop_fn and stop_fn(items):
                break

            count = response['count']
            offset = response['offset']

    def get_all(self, method, max_count, values=None, key='items', limit=None,
                stop_fn=None, negative_offset=False):
        """ Использовать только если нужно загрузить все объекты в память.

        Eсли вы можете обрабатывать объекты по частям, то лучше
        использовать get_all_iter

        Например если вы записываете объекты в БД, то нет смысла загружать
        все данные в память
        """

        items = list(
            self.get_all_iter(
                method, max_count, values, key, limit, stop_fn, negative_offset
            )
        )

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

        :param limit: ограничение на количество получаемых элементов,
                            но может прийти больше
        :type limit: int

        :param stop_fn: функция, отвечающая за выход из цикла
        :type stop_fn: func

        :param negative_offset: True если offset должен быть отрицательный
        :type negative_offset: bool
        """

        values = values.copy() if values else {}
        values['count'] = max_count

        offset_mul = -1 if negative_offset else 1

        offset = max_count if negative_offset else 0
        count = None

        items_count = 0

        while count is None or offset < count:
            values['offset'] = offset * offset_mul
            response = self.vk.method(method, values)

            new_count = response['count']

            count_diff = (new_count - count) if count is not None else 0

            if count_diff < 0:
                offset += count_diff
                count = new_count
                continue

            response_items = response[key]
            items = response_items[count_diff:]
            items_count += len(items)

            for item in items:
                yield item

            if len(response_items) < max_count - count_diff:
                break

            if limit and items_count >= limit:
                break

            if stop_fn and stop_fn(items):
                break

            offset += max_count
            count = new_count

    def get_all_slow(self, method, max_count, values=None, key='items',
                     limit=None, stop_fn=None, negative_offset=False):
        """ Использовать только если нужно загрузить все объекты в память.

        Eсли вы можете обрабатывать объекты по частям, то лучше
        использовать get_all_slow_iter

        Например если вы записываете объекты в БД, то нет смысла загружать
        все данные в память
        """

        items = list(
            self.get_all_slow_iter(
                method, max_count, values, key, limit, stop_fn, negative_offset
            )
        )
        return {'count': len(items), key: items}


vk_get_all_items = VkFunction(
    args=('method', 'key', 'values', 'count', 'offset', 'offset_mul'),
    clean_args=('method', 'key', 'offset', 'offset_mul'),
    return_raw=True,
    code='''
    var params = %(values)s,
        calls = 0,
        items = [],
        count = %(count)s,
        offset = %(offset)s,
        ri;

    while(calls < 25) {
        calls = calls + 1;

        params.offset = offset * %(offset_mul)s;
        var response = API.%(method)s(params),
            new_count = response.count,
            count_diff = (count == null ? 0 : new_count - count);
        if (!response) {
            return {"_error": 1};
        }

        if (count_diff < 0) {
            offset = offset + count_diff;
        } else {
            ri = response.%(key)s;
            items = items + ri.slice(count_diff);
            offset = offset + params.count + count_diff;
            if (ri.length < params.count) {
                calls = 99;
            }
        }

        count = new_count;

        if (count != null && offset >= count) {
            calls = 99;
        }
    };

    return {
        count: count,
        items: items,
        offset: offset,
        more: calls != 99
    };
''')
