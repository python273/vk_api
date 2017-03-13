# -*- coding: utf-8 -*-
"""
@author: Kirill Python
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2017
"""


CAPTCHA_ERROR_CODE = 14


class VkApiError(Exception):
    pass


class AuthorizationError(VkApiError):  # todo: delete
    pass


class AuthError(AuthorizationError):
    pass


class BadPassword(AuthError):
    pass


class AccountBlocked(AuthError):
    pass


class TwoFactorError(AuthError):
    pass


class SecurityCheck(AuthError):
    def __init__(self, phone_prefix=None, phone_postfix=None, response=None):
        self.phone_prefix = phone_prefix
        self.phone_postfix = phone_postfix
        self.response = response

    def __str__(self):
        if self.phone_prefix and self.phone_postfix:
            return 'Security check. Enter number: {} ... {}'.format(
                self.phone_prefix, self.phone_postfix
            )
        else:
            return ('Security check. Phone prefix and postfix not detected. '
                    'Please send bugreport. Response in self.response')


class ApiError(VkApiError):
    def __init__(self, vk, method, values, error):
        self.vk = vk
        self.method = method
        self.values = values
        self.code = error['error_code']
        self.error = error

    def try_method(self):
        """ Пробует отправить запрос заново

        """

        return self.vk.method(self.method, self.values)

    def __str__(self):
        return '[{}] {}'.format(self.error['error_code'],
                                self.error['error_msg'])


class ApiHttpError(VkApiError):
    def __init__(self, vk, method, values, response):
        self.vk = vk
        self.method = method
        self.values = values
        self.response = response

    def try_method(self):
        """ Пробует отправить запрос заново

        """

        return self.vk.method(self.method, self.values)

    def __str__(self):
        return 'Response code {}'.format(self.response.status_code)


class Captcha(VkApiError):
    def __init__(self, vk, captcha_sid, func, args=None, kwargs=None, url=None):
        self.vk = vk
        self.sid = captcha_sid
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}

        self.code = CAPTCHA_ERROR_CODE

        self.key = None
        self.url = url
        self.image = None

    def get_url(self):
        """ Возвращает ссылку на изображение капчи

        """

        if not self.url:
            self.url = 'https://api.vk.com/captcha.php?sid={}'.format(self.sid)

        return self.url

    def get_image(self):
        """ Возвращает бинарное изображение капчи, получаемое по get_url()
        """

        if not self.image:
            self.image = self.vk.http.get(self.get_url()).content

        return self.image

    def try_again(self, key):
        """ Отправляет запрос заново с ответом капчи

        :param key: текст капчи
        """

        if key:
            self.key = key

            self.kwargs.update({
                'captcha_sid': self.sid,
                'captcha_key': self.key
            })

        return self.func(*self.args, **self.kwargs)

    def __str__(self):
        return 'Captcha needed'
