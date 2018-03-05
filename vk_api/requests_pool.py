# -*- coding: utf-8 -*-
"""
@author: python273
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2018
"""

import sys
from collections import namedtuple

from .utils import sjson_dumps
from .execute import VkFunction

if sys.version_info.major == 2:
    range = xrange


class VkRequestsPoolException(Exception):
    pass


PoolRequest = namedtuple('PoolRequest', ['method', 'values', 'result'])


class RequestResult(object):

    __slots__ = ('_result', 'ready', '_error')

    def __init__(self):
        self._result = None
        self.ready = False
        self._error = False

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, value):
        self._error = value
        self.ready = True

    @property
    def result(self):
        if not self.ready:
            raise RuntimeError('Result is not available in `with` context')

        if self._error:
            raise VkRequestsPoolException('Got error while executing request')

        return self._result

    @result.setter
    def result(self, result):
        self._result = result
        self.ready = True

    @property
    def ok(self):
        return self.ready and not self._error


class VkRequestsPool(object):
    """ Позволяет сделать несколько обращений к API за один запрос
        за счет метода execute
    """

    __slots__ = ('vk', 'pool', 'one_param', 'execute_errors')

    def __init__(self, vk):
        self.vk = vk
        self.pool = []
        self.one_param = {}
        self.execute_errors = []

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        if self.one_param:
            self.execute_one_param()
        else:
            self.execute()

    def get_execute_errors(self):
        return self.execute_errors

    def method(self, method, values=None):
        """ Добавляет запрос в пулл

        :param method: метод
        :type method: str

        :param values: параметры
        :type values: dict

        :rtype: RequestResult
        """

        if self.one_param:
            raise RuntimeError('One param mode does not work with self.method')

        if values is None:
            values = {}

        result = RequestResult()
        self.pool.append(PoolRequest(method, values, result))

        return result

    def method_one_param(self, method, key, values, default_values=None):
        """ Использовать, если изменяется значение только одного параметра

        :param method: метод
        :type method: str

        :param default_values: одинаковые значения для запросов
        :type default_values: dict

        :param key: ключ изменяющегося параметра
        :type key: str

        :param values: список значений изменяющегося параметра (max: 25)
        :type values: list

        :rtype: RequestResult
        """

        if not self.one_param and self.pool:
            raise RuntimeError('One param mode does not work with self.method')

        if default_values is None:
            default_values = {}

        self.one_param = {
            'method': method,
            'default': default_values,
            'key': key,
            'return': RequestResult()
        }

        self.pool = values

        return self.one_param['return']

    def execute(self):
        for i in range(0, len(self.pool), 25):
            cur_pool = self.pool[i:i + 25]

            one_method = check_one_method(cur_pool)

            if one_method:
                value_list = [i.values for i in cur_pool]

                response_raw = vk_one_method(self.vk, one_method, value_list)
            else:
                response_raw = vk_many_methods(self.vk, cur_pool)

            response = response_raw['response']
            response_errors = response_raw.get('execute_errors')

            if response_errors:
                self.execute_errors += response_errors[:-1]

            for x, response in enumerate(response):
                if response is not False:
                    cur_pool[x].result.result = response
                else:
                    cur_pool[x].result.error = True

    def execute_one_param(self):
        result = {}

        method = self.one_param['method']
        default = self.one_param['default']
        key = self.one_param['key']

        for i in range(0, len(self.pool), 25):
            cur_pool = self.pool[i:i + 25]

            response_raw = vk_one_param(self.vk, method, cur_pool, default, key)

            response = response_raw['response']
            response_errors = response_raw.get('execute_errors')

            if response_errors:
                self.execute_errors += response_errors[:-1]

            for x, r in enumerate(response):
                if r is not False:
                    result[cur_pool[x]] = r

        self.one_param['return'].result = result


def check_one_method(pool):
    """ Возвращает True, если все запросы в пулле к одному методу """

    if not pool:
        return False

    first_method = pool[0].method

    if all(req.method == first_method for req in pool[1:]):
        return first_method

    return False


vk_one_method = VkFunction(
    args=('method', 'values'),
    clean_args=('method',),
    return_raw=True,
    code='''
    var values = %(values)s,
        i = 0,
        result = [];

    while(i < values.length) {
        result.push(API.%(method)s(values[i]));
        i = i + 1;
    }

    return result;
''')


vk_one_param = VkFunction(
    args=('method', 'values', 'default_values', 'key'),
    clean_args=('method', 'key'),
    return_raw=True,
    code='''
    var def_values = %(default_values)s,
        values = %(values)s,
        result = [],
        i = 0;

    while(i < values.length) {
        def_values.%(key)s = values[i];

        result.push(API.%(method)s(def_values));

        i = i + 1;
    }

    return result;
''')


def vk_many_methods(vk_session, pool):
    requests = ','.join(
        'API.{}({})'.format(i.method, sjson_dumps(i.values))
        for i in pool
    )

    code = 'return [{}];'.format(requests)

    return vk_session.method('execute', {'code': code}, raw=True)
