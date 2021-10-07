# -*- coding: utf-8 -*-
"""
:authors: python273
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2019 python273
"""

from collections import namedtuple

from .exceptions import VkRequestsPoolException
from .execute import VkFunction
from .utils import sjson_dumps

PoolRequest = namedtuple('PoolRequest', ['method', 'values', 'result'])


class RequestResult(object):
    """ Результат запроса из пула """

    __slots__ = ('_result', 'ready', '_error')

    def __init__(self):
        self._result = None
        self.ready = False
        self._error = False

    @property
    def error(self):
        """Ошибка, либо `False`, если запрос прошёл успешно."""
        return self._error

    @error.setter
    def error(self, value):
        self._error = value
        self.ready = True

    @property
    def result(self):
        """Результат запроса, если он прошёл успешно."""
        if not self.ready:
            raise RuntimeError('Result is not available in `with` context')

        if self._error:
            raise VkRequestsPoolException(
                self._error,
                'Got error while executing request: [{}] {}'.format(
                    self.error['error_code'],
                    self.error['error_msg']
                )
            )

        return self._result

    @result.setter
    def result(self, result):
        self._result = result
        self.ready = True

    @property
    def ok(self):
        """`True`, если результат запроса не содержит ошибок, иначе `False`"""
        return self.ready and not self._error


class VkRequestsPool(object):
    """
    Позволяет сделать несколько обращений к API за один запрос
    за счет метода execute.

    Варианты использованя:
    - В качестве менеджера контекста: запросы к API добавляются в
    открытый пул, и выполняются при его закрытии.
    - В качестве объекта пула. запросы к API дабвляются по одному
    в пул и выполняются все вместе при выполнении метода execute()


    :param vk_session: Объект :class:`VkApi`
    """

    __slots__ = ('vk_session', 'pool')

    def __init__(self, vk_session):
        self.vk_session = vk_session
        self.pool = []

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.execute()

    def method(self, method, values=None):
        """ Добавляет запрос в пул.
            Возвращаемое значение будет содержать результат после закрытия пула.

        :param method: метод
        :type method: str

        :param values: параметры
        :type values: dict

        :rtype: RequestResult
        """

        if values is None:
            values = {}

        result = RequestResult()
        self.pool.append(PoolRequest(method, values, result))

        return result

    def execute(self):
        """
        Выполняет все находящиеся в пуле запросы и отчищает пул.
        Необходим для использования пула-объекта.
        Для пула менеджера контекста вызывается автоматически.
        """
        for i in range(0, len(self.pool), 25):
            cur_pool = self.pool[i:i + 25]

            one_method = check_one_method(cur_pool)

            if one_method:
                value_list = [i.values for i in cur_pool]

                response_raw = vk_one_method(
                    self.vk_session, one_method, value_list
                )
            else:
                response_raw = vk_many_methods(self.vk_session, cur_pool)

            response = response_raw['response']
            response_errors = response_raw.get('execute_errors', [])

            response_errors_iter = iter(response_errors)

            for x, current_response in enumerate(response):
                current_result = cur_pool[x].result

                if current_response is not False:
                    current_result.result = current_response
                else:
                    current_result.error = next(response_errors_iter)
        self.pool = []


def check_one_method(pool):
    """ Возвращает True, если все запросы в пуле к одному методу """

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


def vk_many_methods(vk_session, pool):
    requests = ','.join(
        'API.{}({})'.format(i.method, sjson_dumps(i.values))
        for i in pool
    )

    code = 'return [{}];'.format(requests)

    return vk_session.method('execute', {'code': code}, raw=True)


def vk_request_one_param_pool(vk_session, method, key, values,
                              default_values=None):
    """ Использовать, если изменяется значение только одного параметра.
        Возвращаемое значение содержит tuple из dict с результатами и
        dict с ошибками при выполнении

    :param vk_session: объект VkApi
    :type vk_session: vk_api.VkAPi

    :param method: метод
    :type method: str

    :param default_values: одинаковые значения для запросов
    :type default_values: dict

    :param key: ключ изменяющегося параметра
    :type key: str

    :param values: список значений изменяющегося параметра (max: 25)
    :type values: list

    :rtype: (dict, dict)
    """

    result = {}
    errors = {}

    if default_values is None:
        default_values = {}

    for i in range(0, len(values), 25):
        current_values = values[i:i + 25]

        response_raw = vk_one_param(
            vk_session, method, current_values, default_values, key
        )

        response = response_raw['response']
        response_errors = response_raw.get('execute_errors', [])
        response_errors_iter = iter(response_errors)

        for x, r in enumerate(response):
            if r is not False:
                result[current_values[x]] = r
            else:
                errors[current_values[x]] = next(response_errors_iter)

    return result, errors


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
