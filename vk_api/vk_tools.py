# encoding: utf-8

"""
@author: Kirill Python
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2015
"""

import json
import sys

if sys.version_info[0] != 3:
    range = xrange  # @ReservedAssignment @UndefinedVariable


class VkTools(object):
    def __init__(self, vk):
        """

        :param vk: объект VkApi
        """

        self.vk = vk

    def get_all(self, method, max_count, values=None, key='items',
                limit_count=None):
        """ Получить все элементы
        Работает в методах, где в ответе есть count и items или users
        За один запрос получает max_count * 25 элементов

        :param method: метод
        :param values: параметры
        :param max_count: максимальное количество элементов,
                            которое можно получить за один раз
        :param key: ключ элементов, которые нужно получить
        :param limit_count: ограничение на кол-во получаемых элементов,
                            но может прийти больше
        """

        if values:
            values = values.copy()
        else:
            values = {}

        items = []
        offset = 0

        while True:
            run_code = code_get_all_items % (max_count, offset, key,
                                             json.dumps(values),
                                             method, method)

            response = self.vk.method('execute', {'code': run_code})

            items += response['items']

            if response['offset'] >= response['count']:
                break

            if limit_count and len(items) >= limit_count:
                break

            offset = response['offset']

        return {'count': len(items), key: items}

    def get_all_slow(self, method, values=None, max_count=200, key='items'):
        """ Получить все элементы
        Работает в методах, где в ответе есть count и items или users

        :param method: метод
        :param values: параметры
        :param max_count: максимальное количество элементов,
                            которое можно получить за один раз
        :param key: ключ элементов, которые нужно получить
        """

        if not values:
            values = {}
        else:
            values = values.copy()

        values.update({'count': max_count})

        response = self.vk.method(method, values)
        count = response['count']
        items = response[key]

        for i in range(max_count, count + 1, max_count):
            values.update({
                'offset': i
            })

            response = self.vk.method(method, values)
            items += response[key]

        return {'count': len(items), key: items}

# Полный код в файле vk_procedures
code_get_all_items = """
var m=%s,n=%s,b="%s",v=n;var c={count:m,offset:v}+%s;var r=API.%s(c),k=r.count,
j=r[b],i=1;while(i<25&&v+m<=k){v=i*m+n;c.offset=v;j=j+API.%s(c)[b];i=i+1;}
return {count:k,items:j,offset:v+m};
""".replace('\n', '')
