# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2016
"""

try:
    import simplejson as json
except ImportError:
    import json


def search_re(reg, string):
    """ Поиск по регулярке """
    s = reg.search(string)

    if s:
        groups = s.groups()
        return groups[0]


def clean_string(s):
    if s:
        return s.strip().replace('&nbsp;', '')


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