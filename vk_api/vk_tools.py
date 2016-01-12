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
    """ Содержит некоторые воспомогательные функции, которые могут понадобиться
        при использовании API
    """

    __slots__ = ('vk',)

    def __init__(self, vk):
        """
        :param vk: объект VkApi
        """
        self.vk = vk

    def get_all(self, method, max_count, values=None, key='items', limit=None):
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

        items = []
        offset = 0

        while True:
            run_code = code_get_all_items % (
                max_count, offset, key, json.dumps(values, ensure_ascii=False),
                method, method
            )

            response = self.vk.method('execute', {'code': run_code})

            items += response['items']
            offset = response['offset']

            if offset >= response['count']:
                break

            if limit and len(items) >= limit:
                break

        return {'count': len(items), key: items}

    def get_all_slow(self, method, max_count, values=None, key='items',
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
        items = response[key]

        for i in range(max_count, count + 1, max_count):
            values.update({
                'offset': i
            })

            response = self.vk.method(method, values)
            items += response[key]

            if limit and len(items) >= limit:
                break

        return {'count': len(items), key: items}


class VkRequestsPool(object):
    """ Позволяет сделать несколько обращений к API за один запрос
        за счет метода execute
    """

    __slots__ = ('vk', 'pool', 'one_param')

    def __init__(self, vk):
        self.vk = vk
        self.pool = []
        self.one_param = False

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.execute()

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
        if len(pool) > 1:
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
        json_list_values = json.dumps(list_values, separators=(',', ':'))
        run_code = code_requestspoll_one_method % (
            json_list_values, method
        )

        return run_code

    def gen_code_one_param(self, pool):
        """ Генерирует код для одного метода и одного меняющегося параметра
           (если в пулле запросы к одному методу, с одним меняющеися параметром)
        """
        run_code = code_requestspoll_one_param % (
            json.dumps(self.one_param['default'], separators=(',', ':')),
            json.dumps(pool, separators=(',', ':')),
            self.one_param['key'],
            self.one_param['method']
        )

        # print(run_code)

        return run_code

    def gen_code_many_methods(self, pool):
        """ Генерирует код для нескольких методов """
        reqs = ','.join(
            'API.{}({})'.format(i[0], json.dumps(i[1]), separators=(',', ':'))
            for i in pool
        )
        run_code = 'return [{}];'.format(reqs)

        return run_code

    def execute(self):
        for i in range(0, len(self.pool), 25):
            cur_pool = self.pool[i:i + 25]

            if self.one_param:
                run_code = self.gen_code_one_param(cur_pool)
            else:
                one_method = self.check_one_method(cur_pool)

                if one_method:
                    run_code = self.gen_code_one_method(cur_pool)
                else:
                    run_code = self.gen_code_many_methods(cur_pool)

            response = self.vk.method('execute', {'code': run_code})

            for x in range(len(response)):
                if self.one_param:
                    self.one_param['return'][cur_pool[x]] = response[x]
                else:
                    self.pool[i + x][2].update(response[x])


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
