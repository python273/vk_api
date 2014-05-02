# encoding: utf-8

"""
@author: Kirill Python
@contact: http://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2014
"""

import json
import sys

if sys.version_info[0] == 3:
    xrange = range


class VkTools(object):
    def __init__(self, vk):
        self.vk = vk

    def get_all(self, method, values=None, max_count=200, key='items'):
        """ Получить все элементы
            Работает в методах, где в ответе есть items или users
            За один запрос получает max_count * 25 элементов

        :param method: метод
        :param values: параметры
        :param max_count: максимальное количество элементов,
                            которое можно получить за один раз
        :param key: ключ элементов, которые нужно получить
        """

        if values:
            values = values.copy()
        else:
            values = {}

        items = []
        offset = 0

        while True:
            run_code = code_get_all_items % (
                                        max_count, offset, json.dumps(values),
                                        key, method, method
                                    )

            response = self.vk.method('execute', {'code': run_code})

            items += response['items']

            if response['end']:
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

        for i in xrange(max_count, count + 1, max_count):
            values.update({
                'offset': i
            })

            response = self.vk.method(method, values)
            items += response[key]

        return {'count': len(items), key: items}

# Полный код в файле vk_procedures
code_get_all_items = '''
var z=%s,x=%s,y=%s,k="%s",p={"count":z}+y,r=API.%s(p),c=r["count"],j=r[k],o=0,
i=1;while(i<25&&o<c){o=i*z+x;p={"count":z,"offset":o}+y;r=API.%s(p);j=j+r[k];i
=i+1;};return{"count":c,"items":j,"offset":o,"end":o+z>=c};
'''.replace('\n', '')
