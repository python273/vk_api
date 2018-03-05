# -*- coding: utf-8 -*-
"""
@author: python273
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2018
"""

from .utils import sjson_dumps
from .vk_api import VkApi, VkApiMethod


class VkFunction(object):

    __slots__ = ('code', '_minified_code', 'args', 'clean_args', 'return_raw')

    def __init__(self, code, args=None, clean_args=None, return_raw=False):
        """ Обертка над методом execute

        :param code: код функции (VKScript)
        :param args: список аргументов (будут конвертированы в JSON)
        :param clean_args: список raw аргументов (будут вставлены как строки)
        :param return_raw: аргумент raw функции VkApi.method
        """

        self.code = code
        self._minified_code = minify(code)

        self.args = () if args is None else args
        self.clean_args = () if clean_args is None else clean_args

        self.return_raw = return_raw

    def compile(self, args):
        compiled_args = {}

        for key, value in args.items():
            if key in self.clean_args:
                compiled_args[key] = str(value)
            else:
                compiled_args[key] = sjson_dumps(value)

        return self._minified_code % compiled_args

    def __call__(self, vk, *args, **kwargs):

        if not isinstance(vk, (VkApi, VkApiMethod)):
            raise TypeError(
                'The first arg should be VkApi or VkApiMethod instance'
            )

        if isinstance(vk, VkApiMethod):
            vk = vk._vk

        args = parse_args(self.args, args, kwargs)

        return vk.method(
            'execute',
            {'code': self.compile(args)},
            raw=self.return_raw
        )


def minify(code):
    return ''.join(i.strip() for i in code.splitlines())


def parse_args(function_args, args, kwargs):
    parsed_args = {}

    for arg_name in kwargs.keys():
        if arg_name in function_args:
            parsed_args[arg_name] = kwargs[arg_name]
        else:
            raise VkFunctionException(
                'function got an unexpected keyword argument \'{}\''.format(
                    arg_name
                ))

    args_count = len(args) + len(kwargs)
    func_args_count = len(function_args)

    if args_count != func_args_count:
        raise VkFunctionException(
            'function takes exactly {} argument{} ({} given)'.format(
                func_args_count,
                's' if func_args_count > 1 else '',
                args_count
            ))

    for arg_name, arg_value in zip(function_args, args):
        parsed_args[arg_name] = arg_value

    return parsed_args


class VkFunctionException(Exception):
    pass
