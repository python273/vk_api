# -*- coding: utf-8 -*-

import sys
from collections import namedtuple

from .utils import sjson_dumps

if sys.version_info.major == 2:
    range = xrange

PoolRequest = namedtuple('PoolRequest', ['method', 'values', 'result'])


class RequestResult(object):
    def __init__(self):
        self._result = None
        self.ready = False
        self.error = False

    def set_result(self, result):
        self._result = result
        self.ready = True

    def set_error(self, error):
        self.error = error
        self.ready = True

    @property
    def ok(self):
        return not self.error

    @property
    def result(self):
        if not self.ready:
            raise Exception('Result is not ready')

        if self.error:
            raise Exception('Got error while executing request')

        return self._result


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
            raise Exception('One param mode is not working with self.method')

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
            raise Exception('One param mode is not working with self.method')

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

            if check_one_method(cur_pool):
                code = gen_code_one_method(cur_pool)
            else:
                code = gen_code_many_methods(cur_pool)

            response_raw = self.vk.method('execute', {'code': code}, raw=True)

            response = response_raw['response']
            response_errors = response_raw.get('execute_errors')

            if response_errors:
                self.execute_errors += response_errors[:-1]

            for x, r in enumerate(response):
                if r is not False:
                    cur_pool[x].result.set_result(r)
                else:
                    cur_pool[x].result.set_error(True)

    def execute_one_param(self):
        result = {}

        for i in range(0, len(self.pool), 25):
            cur_pool = self.pool[i:i + 25]

            code = gen_code_one_param(
                cur_pool,
                self.one_param['default'],
                self.one_param['key'],
                self.one_param['method']
            )

            response_raw = self.vk.method('execute', {'code': code}, raw=True)

            response = response_raw['response']
            response_errors = response_raw.get('execute_errors')

            if response_errors:
                self.execute_errors += response_errors[:-1]

            for x, r in enumerate(response):
                if r is not False:
                    result[cur_pool[x]] = r

        self.one_param['return'].set_result(result)


def check_one_method(pool):
    """ Возвращает True, если все запросы в пулле к одному методу """

    if not pool:
        return False

    first_method = pool[0].method
    return all(req.method == first_method for req in pool[1:])


def gen_code_one_method(pool):
    """ Генерирует код для одного метода
        (если в пулле запросы к одному методу)
    """

    method = pool[0].method
    list_values = [i.values for i in pool]

    return code_requestspoll_one_method % (
        sjson_dumps(list_values), method
    )


def gen_code_one_param(pool, default_values, key, method):
    """ Генерирует код для одного метода и одного меняющегося параметра
       (если в пулле запросы к одному методу, с одним меняющимся параметром)
    """

    return code_requestspoll_one_param % (
        sjson_dumps(default_values),
        sjson_dumps(pool),
        key,
        method
    )


def gen_code_many_methods(pool):
    """ Генерирует код для нескольких методов """

    requests = ','.join(
        'API.{}({})'.format(i.method, sjson_dumps(i.values))
        for i in pool
    )

    return 'return [{}];'.format(requests)


# Полный код в файле vk_procedures
code_requestspoll_one_method = """
var p=%s,i=0,r=[];while(i<p.length){r.push(API.%s(p[i]));i=i+1;}return r;
""".replace('\n', '')

code_requestspoll_one_param = """
var d=%s,v=%s,r=[],i=0;while(i<v.length){d.%s=v[i];r.push(API.%s(d));i=i+1;};
return r;
""".replace('\n', '')
