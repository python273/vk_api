# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2016
"""


def doc(method=None):
    """ Открывает документацию на метод или список всех методов

    :param method: метод
    """

    if not method:
        method = 'methods'

    url = 'https://vk.com/dev/{}'.format(method)

    import webbrowser
    webbrowser.open(url)


def search_re(reg, string):
    """ Поиск по регулярке """
    s = reg.search(string)

    if s:
        groups = s.groups()
        return groups[0]


def clean_string(s):
    if s:
        return s.strip().replace('&nbsp;', '')


def code_from_number(phone_prefix, phone_postfix, number):
    prefix_len = len(phone_prefix)
    postfix_len = len(phone_postfix)

    if number[0] == '+':
        number = number[1:]

    if (prefix_len + postfix_len) >= len(number):
        return

    # Сравниваем начало номера
    if not number[:prefix_len] == phone_prefix:
        return

    # Сравниваем конец номера
    if not number[-postfix_len:] == phone_postfix:
        return

    return number[prefix_len:-postfix_len]