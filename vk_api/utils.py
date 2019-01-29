# -*- coding: utf-8 -*-
"""
:authors: python273
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2019 python273
"""

from __future__ import print_function

import random

import six

try:
    import simplejson as json
except ImportError:
    import json

try:
    from http.cookiejar import Cookie
except ImportError:  # python2
    from cookielib import Cookie


def search_re(reg, string):
    """ Поиск по регулярке """
    s = reg.search(string)

    if s:
        groups = s.groups()
        return groups[0]


def clear_string(s):
    if s:
        return s.strip().replace('&nbsp;', '')


def get_random_id():
    """ Get random int32 number (signed) """
    return random.getrandbits(31) * random.choice([-1, 1])


def code_from_number(prefix, postfix, number):
    prefix_len = len(prefix)
    postfix_len = len(postfix)

    if number[0] == '+':
        number = number[1:]

    if (prefix_len + postfix_len) >= len(number):
        return

    # Сравниваем начало номера
    if number[:prefix_len] != prefix:
        return

    # Сравниваем конец номера
    if number[-postfix_len:] != postfix:
        return

    return number[prefix_len:-postfix_len]


def sjson_dumps(*args, **kwargs):
    kwargs['ensure_ascii'] = False
    kwargs['separators'] = (',', ':')

    return json.dumps(*args, **kwargs)


HTTP_COOKIE_ARGS = [
    'version', 'name', 'value',
    'port', 'port_specified',
    'domain', 'domain_specified',
    'domain_initial_dot',
    'path', 'path_specified',
    'secure', 'expires', 'discard', 'comment', 'comment_url', 'rest', 'rfc2109'
]


def cookie_to_dict(cookie):
    cookie_dict = {
        k: v for k, v in six.iteritems(cookie.__dict__) if k in HTTP_COOKIE_ARGS
    }

    cookie_dict['rest'] = cookie._rest
    cookie_dict['expires'] = None

    return cookie_dict


def cookie_from_dict(d):
    return Cookie(**d)


def cookies_to_list(cookies):
    return [cookie_to_dict(cookie) for cookie in cookies]


def set_cookies_from_list(cookie_jar, l):
    for cookie in l:
        cookie_jar.set_cookie(cookie_from_dict(cookie))


def enable_debug_mode(vk_session, print_content=False):
    """ Включает режим отладки:
        - Вывод сообщений лога
        - Вывод http запросов

    :param vk_session: объект VkApi
    :param print_content: печатать ответ http запросов
    """

    import logging
    import sys
    import time

    import requests

    from . import __version__

    pypi_version = requests.get(
        'https://pypi.org/pypi/vk_api/json'
    ).json()['info']['version']

    if __version__ != pypi_version:
        print()
        print('######### MODULE IS NOT UPDATED!!1 ##########')
        print()
        print('Installed vk_api version is:', __version__)
        print('PyPI vk_api version is:', pypi_version)
        print()
        print('######### MODULE IS NOT UPDATED!!1 ##########')
        print()

    class DebugHTTPAdapter(requests.adapters.HTTPAdapter):
        def send(self, request, **kwargs):
            start = time.time()
            response = super(DebugHTTPAdapter, self).send(request, **kwargs)
            end = time.time()

            total = end - start

            print(
                '{:0.2f} {} {} {} {}'.format(
                    total,
                    request.method,
                    request.url,
                    response.status_code,
                    response.history
                )
            )

            if print_content:
                print(response.text)

            return response

    vk_session.http.mount('http://', DebugHTTPAdapter())
    vk_session.http.mount('https://', DebugHTTPAdapter())

    vk_session.logger.setLevel(logging.INFO)
    vk_session.logger.addHandler(logging.StreamHandler(sys.stdout))
