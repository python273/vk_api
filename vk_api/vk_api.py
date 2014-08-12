# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: http://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2014
"""

import jconfig
import re
import requests
import time

DELAY = 1.0 / 3  # 3 requests per second
CAPTCHA_ERROR_CODE = 14
NEED_VALIDATION_CODE = 17


class VkApi(object):
    def __init__(self, login=None, password=None, number=None, token=None,
                 proxies=None, captcha_handler=None, config_filename=None,
                 api_version='5.21', app_id=2895443, scope=2097151):
        """
        :param login: Логин ВКонтакте
        :param password: Пароль ВКонтакте
        :param number: Номер для проверке безопасности (указывать, если
                                     в качестве логина используется не номер)

        :param token: access_token
        :param proxies: proxy server
                        {'http': 'http://127.0.0.1:8888/',
                        'https': 'https://127.0.0.1:8888/'}
        :param captcha_handler: Функция для обработки капчи
        :param config_filename: Расположение config файла

        :param api_version: Версия API (default: '5.21')
        :param app_id: Standalone-приложение (default: 2895443)
        :param scope: Запрашиваемые права (default: 2097151)
        """

        self.login = login
        self.password = password
        self.number = number

        self.sid = None
        self.token = {'access_token': token}

        self.api_version = api_version
        self.app_id = app_id
        self.scope = scope

        self.settings = jconfig.Config(login, filename=config_filename)

        self.http = requests.Session()
        self.http.proxies = proxies  # Ставим прокси
        self.http.headers = {  # Притворимся браузером
            'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:28.0) ' \
                                            'Gecko/20100101 Firefox/28.0'
        }
        self.http.verify = False

        self.last_request = 0.0

        self.error_handlers = {
            NEED_VALIDATION_CODE: self.need_validation_handler,
            CAPTCHA_ERROR_CODE: captcha_handler or self.captcha_handler
        }

        if login and password:
            self.sid = self.settings['remixsid']
            self.token = self.settings['access_token']

            if not self.check_sid():
                self.vk_login()
            else:
                self.security_check('http://vk.com')

            if not self.check_token():
                self.api_login()

    def vk_login(self, captcha_sid=None, captcha_key=None):
        """ Авторизцаия ВКонтакте с получением cookies remixsid """

        url = 'https://login.vk.com/'
        values = {
            'act': 'login',
            'utf8': '1',
            'email': self.login,
            'pass': self.password
        }

        if captcha_sid and captcha_key:
            values.update({
                'captcha_sid': captcha_sid,
                'captcha_key': captcha_key
            })

        self.http.cookies.clear()
        response = self.http.post(url, values)

        if 'remixsid' in self.http.cookies:
            remixsid = self.http.cookies['remixsid']
            self.settings['remixsid'] = remixsid

            # Нужно для авторизации в API
            self.settings['forapilogin'] = {
                'p': self.http.cookies['p'],
                'l': self.http.cookies['l']
            }

            self.sid = remixsid

        elif 'sid=' in response.url:
            captcha_sid = regexp(r'sid=(\d+)', response.url)[0]
            captcha = Captcha(self, captcha_sid, self.vk_login)

            if self.error_handlers[CAPTCHA_ERROR_CODE]:
                self.error_handlers[CAPTCHA_ERROR_CODE](captcha)
            else:
                raise AuthorizationError('Authorization error (capcha)')
        else:
            raise BadPassword('Bad password')

        if 'security_check' in response.url:
            self.security_check(response=response)

    def security_check(self, url=None, response=None):
        if url:
            response = self.http.get(url)
            if not 'security_check' in response.url:
                return

        phone_prefix = regexp(r'phone_number">(.*?)<',
                              response.text)
        phone_prefix = phone_prefix[0].strip()

        phone_postfix = regexp(r'phone_postfix">(.*?)<',
                               response.text)
        phone_postfix = phone_postfix[0].strip()

        if self.number:
            code = code_from_number(phone_prefix, phone_postfix, self.number)
        else:
            code = code_from_number(phone_prefix, phone_postfix, self.login)

        if code:
            number_hash = regexp(r'security_check.*?hash: \'(.*?)\'\};',
                                 response.text)[0]

            values = {
                'act': 'security_check',
                'al': '1',
                'al_page': '3',
                'code': code,
                'hash': number_hash,
                'to': ''
            }

            response = self.http.post('https://vk.com/login.php', values)

            if response.text.split('<!>')[4] == '4':
                return True

        raise SecurityCheck(phone_prefix, phone_postfix)

    def check_sid(self):
        """ Прверка Cookies remixsid на валидность """

        if self.sid:
            url = 'https://vk.com/feed2.php'
            self.http.cookies.update({
                'remixsid': self.sid,
                'remixlang': '0',
                'remixsslsid': '1'
            })

            response = self.http.get(url).json()

            if response['user']['id'] != -1:
                return response

    def api_login(self):
        """ Получение токена через Desktop приложение """

        url = 'https://oauth.vk.com/authorize'
        values = {
            'client_id': self.app_id,
            'scope': self.scope,
            'response_type': 'token',
        }

        self.http.cookies.update(self.settings['forapilogin'])
        self.http.cookies.update({'remixsid': self.sid})

        response = self.http.post(url, values)

        if not 'access_token' in response.url:
            url = regexp(r'location\.href = "(.*?)"\+addr;', response.text)[0]
            response = self.http.get(url)

        if 'access_token' in response.url:
            params = response.url.split('#')[1].split('&')

            token = {}
            for i in params:
                x = i.split('=')
                token.update({x[0]: x[1]})

            self.settings['access_token'] = token
            self.token = token
        else:
            raise AuthorizationError('Authorization error (api)')

    def check_token(self):
        """ Прверка access_token на валидность """

        if self.token:
            try:
                self.method('isAppUser')
            except ApiError:
                return False

            return True

    def captcha_handler(self, captcha):
        """ http://vk.com/dev/captcha_error """
        pass

    def need_validation_handler(self, error):
        """ http://vk.com/dev/need_validation """
        # TODO: write me
        pass

    def method(self, method, values=None, captcha_sid=None, captcha_key=None):
        """ Использование методов API

        :param method: метод
        :param values: параметры
        :param captcha_sid:
        :param captcha_key:
        """

        url = 'https://api.vk.com/method/%s' % method

        if values:
            values = values.copy()
        else:
            values = {}

        if not 'v' in values:
            values.update({'v': self.api_version})

        if self.token:
            values.update({'access_token': self.token['access_token']})

        if captcha_sid and captcha_key:
            values.update({
                'captcha_sid': captcha_sid,
                'captcha_key': captcha_key
            })

        # Ограничение 3 запроса в секунду
        delay = DELAY - (time.time() - self.last_request)

        if delay > 0:
            time.sleep(delay)

        response = self.http.post(url, values).json()
        self.last_request = time.time()

        if 'error' in response:
            error = ApiError(self, method, values, response['error'])
            error_code = error.code

            if error_code in self.error_handlers:
                if error_code == CAPTCHA_ERROR_CODE:
                    # TODO: wtf
                    error = Captcha(
                        self,
                        error.error['captcha_sid'],
                        self.method,
                        (method,),
                        {'values': values},
                        error.error['captcha_img']
                    )

                response = self.error_handlers[error_code](error)

                if response is not None:
                    return response

            raise error
        else:
            return response['response']


def regexp(reg, string):
    """ Поиск по регулярке """

    reg = re.compile(reg, re.IGNORECASE | re.DOTALL)
    reg = reg.findall(string)
    return reg


def code_from_number(phone_prefix, phone_postfix, number):
    prefix_len = len(phone_prefix)
    postfix_len = len(phone_postfix)

    if (prefix_len + postfix_len) > len(number):
        return

    # Сравниваем начало номера
    if not number[:prefix_len] == phone_prefix:
        return

    # Сравниваем конец номера
    if not number[-postfix_len:] == phone_postfix:
        return

    return number[prefix_len:-postfix_len]


class AuthorizationError(Exception):
    pass


class BadPassword(AuthorizationError):
    pass


class SecurityCheck(AuthorizationError):
    def __init__(self, phone_prefix, phone_postfix):
        self.phone_prefix = phone_prefix
        self.phone_postfix = phone_postfix

    def __str__(self):
        return 'Security check. Enter number: {}...{}'.format(
            self.phone_prefix, self.phone_postfix
        )


class ApiError(Exception):
    def __init__(self, vk, method, values, error):
        self.vk = vk
        self.method = method
        self.values = values
        self.code = error['error_code']
        self.error = error

    def try_method(self):
        return self.vk.method(self.method, self.values)

    def __str__(self):
        return '[{}] {}'.format(self.error['error_code'],
                                self.error['error_msg'])


class Captcha(Exception):
    def __init__(self, vk, captcha_sid,
                 func, args=None, kwargs=None, url=None):
        self.vk = vk
        self.sid = captcha_sid
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}

        self.key = None
        self.url = url

    def get_url(self):
        if not self.url:
            self.url = 'http://api.vk.com/captcha.php?sid={}'.format(self.sid)

        return self.url

    def try_again(self, key):
        self.key = key

        self.kwargs.update({
            'captcha_sid': self.sid,
            'captcha_key': self.key
        })

        return self.func(*self.args, **self.kwargs)

    def __str__(self):
        return 'Captcha needed'
