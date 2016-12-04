# encoding: utf-8

"""
@author: Kirill Python
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2016
"""

import sys

from .utils import sjson_dumps


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
            run_code = code_get_all_items % (
                max_count, offset, key, sjson_dumps(values),
                method, method
            )

            response = self.vk.method('execute', {'code': run_code})

            items = response['items']
            offset = response['offset']
            items_count += len(items)

            for item in items:
                yield item

            if offset >= response['count']:
                break

            if limit and len(items) >= limit:
                break

    def get_all(self, method, max_count, values=None, key='items', limit=None):
        """ Для обратной совместимости, используйте get_all

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

        items = list(self.get_all_slow(method, max_count, values, key, limit))
        return {'count': len(items), key: items}


# Полный код в файле vk_procedures
code_get_all_items = """
var m=%s,n=%s,b="%s",v=n;var c={count:m,offset:v}+%s;var r=API.%s(c),k=r.count,
j=r[b],i=1;while(i<25&&v+m<=k){v=i*m+n;c.offset=v;j=j+API.%s(c)[b];i=i+1;}
return {count:k,items:j,offset:v+m};
""".replace('\n', '')
