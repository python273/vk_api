# encoding: utf-8

"""
@author: Kirill Python
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2016
"""

import json
import sys

if sys.version_info[0] != 3:
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
        :param values: параметры
        :param max_count: максимальное количество элементов,
                            которое можно получить за один раз
        :param key: ключ элементов, которые нужно получить
        :param limit: ограничение на кол-во получаемых элементов,
                            но может прийти больше
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


class VkRequestsPool(object):
    """ Позволяет сделать несколько обращений к API за один запрос
        за счет метода execute

        Если ответ от API приходит в виде list (например при вызове users.get),
        то значение записывается с ключем list {'list': [...]}
    """

    __slots__ = ('vk', 'pool', 'one_param', 'execute_errors')

    def __init__(self, vk):
        self.vk = vk
        self.pool = []
        self.one_param = False
        self.execute_errors = []

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.execute()

    def get_execute_errors(self):
        return self.execute_errors

    def method(self, method, values=None):
        """ Добавляет запрос в пулл

        :param method: метод
        :param values: параметры
        """

        if self.one_param:
            raise Exception('One param mode dont work with self.method')

        req = (method, values, {})
        self.pool.append(req)
        return req[2]

    def method_one_param(self, method, default_values=None, key=None,
                         values=None):
        """  Использовать, если изменяется значение только одного параметра

        :param method: метод
        :param default_values: одинаковые значения для запросов
        :param key: ключ изменяющегося параметра
        :param values: список значений изменяющегося параметра (max: 25)
        """

        if self.one_param is False and self.pool:
            raise Exception('One param mode dont work with self.method')

        if default_values is None:
            default_values = {}

        self.one_param = {
            'method': method,
            'default': default_values,
            'key': key,
            'return': {}
        }

        self.pool = values

        return self.one_param['return']

    def check_one_method(self, pool):
        """ Возвращает True, если все запросы в пулле к одному методу """
        if pool:
            first_method = pool[0][0]

            for req in pool[1:]:
                if req[0] != first_method:
                    break
            else:
                return True

        return False

    def gen_code_one_method(self, pool):
        """ Генерирует код для одного метода
            (если в пулле запросы к одному методу)
        """
        method = pool[0][0]

        list_values = [i[1] for i in pool]
        json_list_values = sjson_dumps(list_values)
        run_code = code_requestspoll_one_method % (
            json_list_values, method
        )

        return run_code

    def gen_code_one_param(self, pool):
        """ Генерирует код для одного метода и одного меняющегося параметра
           (если в пулле запросы к одному методу, с одним меняющеися параметром)
        """
        run_code = code_requestspoll_one_param % (
            sjson_dumps(self.one_param['default']),
            sjson_dumps(pool),
            self.one_param['key'],
            self.one_param['method']
        )

        # print(run_code)

        return run_code

    def gen_code_many_methods(self, pool):
        """ Генерирует код для нескольких методов """
        reqs = ','.join(
            'API.{}({})'.format(i[0], sjson_dumps(i[1]))
            for i in pool
        )
        run_code = 'return [{}];'.format(reqs)

        return run_code

    def execute(self):
        for i in range(0, len(self.pool), 25):
            cur_pool = self.pool[i:i + 25]

            if self.one_param:
                run_code = self.gen_code_one_param(cur_pool)
            elif self.check_one_method(cur_pool):
                run_code = self.gen_code_one_method(cur_pool)
            else:
                run_code = self.gen_code_many_methods(cur_pool)

            response_raw = self.vk.method('execute', {'code': run_code},
                                          raw=True)

            response = response_raw['response']
            response_errors = response_raw.get('execute_errors')

            if response_errors:
                self.execute_errors += response_errors[:-1]

            for x in range(len(response)):
                if self.one_param:
                    if response[x] is False:
                        self.one_param['return'][cur_pool[x]] = {'_error': True}
                    else:
                        self.one_param['return'][cur_pool[x]] = response[x]
                else:
                    if response[x] is False:
                        self.pool[i + x][2].update({'_error': True})
                    elif type(response[x]) is list:
                        self.pool[i + x][2].update({'list': response[x]})
                    else:
                        self.pool[i + x][2].update(response[x])


def sjson_dumps(*args, **kwargs):
    kwargs['ensure_ascii'] = False
    kwargs['separators'] = (',', ':')

    return json.dumps(*args, **kwargs)

# Полный код в файле vk_procedures
code_get_all_items = """
var m=%s,n=%s,b="%s",v=n;var c={count:m,offset:v}+%s;var r=API.%s(c),k=r.count,
j=r[b],i=1;while(i<25&&v+m<=k){v=i*m+n;c.offset=v;j=j+API.%s(c)[b];i=i+1;}
return {count:k,items:j,offset:v+m};
""".replace('\n', '')

code_requestspoll_one_method = """
var p=%s,i=0,r=[];while(i<p.length){r.push(API.%s(p[i]));i=i+1;}return r;
""".replace('\n', '')

code_requestspoll_one_param = """
var d=%s,v=%s,r=[],i=0;while(i<v.length){d.%s=v[i];r.push(API.%s(d));i=i+1;};
return r;
""".replace('\n', '')
