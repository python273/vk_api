# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2015
"""

import jconfig
import re
import requests
import time

DELAY = 0.36  # 3 requests per second
TOO_MANY_RPS_CODE = 6
CAPTCHA_ERROR_CODE = 14
NEED_VALIDATION_CODE = 17
HTTP_ERROR_CODE = -1

RE_LOGIN_HASH = re.compile(r'name="lg_h" value="([a-z0-9]+)"')
RE_CAPTCHAID = re.compile(r'sid=(\d+)')
RE_NUMBER_HASH = re.compile(r"al_page: '3', hash: '([a-z0-9]+)'")
RE_TOKEN_URL = re.compile(r'location\.href = "(.*?)"\+addr;')

RE_PHONE_PREFIX = re.compile(r'phone_number">(.*?)<')
RE_PHONE_PREFIX_2 = re.compile(r'label ta_r">\+(\d+)')
RE_PHONE_POSTFIX = re.compile(r'phone_postfix">.*?(\d+).*?<')


class VkApi(object):

    def __init__(self, login=None, password=None, number=None, sec_number=None,
                 token=None,
                 proxies=None, captcha_handler=None, config_filename=None,
                 api_version='5.33', app_id=2895443, scope=2097151):
        """
        :param login: Логин ВКонтакте
        :param password: Пароль ВКонтакте
        :param number: Номер для проверки безопасности (указывать, если
                        в качестве логина используется не номер)
        :param sec_number: Часть номера, которая проверяется при проверке
                            безопасности (указывать, если точно известно, что
                            вводить и если автоматическое получение кода из
                            номера работает не корректно)

        :param token: access_token
        :param proxies: proxy server
                        {'http': 'http://127.0.0.1:8888/',
                        'https': 'https://127.0.0.1:8888/'}
        :param captcha_handler: Функция для обработки капчи
        :param config_filename: Расположение config файла

        :param api_version: Версия API (default: '5.33')
        :param app_id: Standalone-приложение (default: 2895443)
        :param scope: Запрашиваемые права (default: 2097151)
        """

        self.login = login
        self.password = password
        self.number = number
        self.sec_number = sec_number

        self.sid = None
        self.token = {'access_token': token}

        self.api_version = api_version
        self.app_id = app_id
        self.scope = scope

        if not config_filename:
            config_filename = 'vk_config.json'

        self.settings = jconfig.Config(login, filename=config_filename)

        self.http = requests.Session()
        self.http.proxies = proxies  # Ставим прокси
        self.http.headers = {  # Притворимся браузером
            'User-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) '
            'Gecko/20100101 Firefox/38.0'
        }

        self.last_request = 0.0

        self.error_handlers = {
            NEED_VALIDATION_CODE: self.need_validation_handler,
            CAPTCHA_ERROR_CODE: captcha_handler or self.captcha_handler,
            TOO_MANY_RPS_CODE: self.too_many_rps_handler
        }

    def authorization(self):
        """ Полная авторизация с получением токена """
        if self.login and self.password:
            self.sid = self.settings['remixsid']
            self.token = self.settings['access_token']

            if not self.check_sid():
                self.vk_login()
            else:
                self.security_check('https://vk.com/')

            if not self.check_token():
                self.api_login()

    def vk_login(self, captcha_sid=None, captcha_key=None):
        """ Авторизация ВКонтакте с получением cookies remixsid """

        self.http.cookies.clear()

        # Get cookies
        response = self.http.get('https://vk.com/')

        values = {
            'act': 'login',
            'email': self.login,
            'pass': self.password,
            'lg_h': search_re(RE_LOGIN_HASH, response.text)
        }

        if captcha_sid and captcha_key:
            values.update({
                'captcha_sid': captcha_sid,
                'captcha_key': captcha_key
            })

        response = self.http.post('https://login.vk.com/', values)

        remixsid = None

        if 'remixsid' in self.http.cookies:
            remixsid = self.http.cookies['remixsid']
        elif 'remixsid6' in self.http.cookies:  # ipv6?
            remixsid = self.http.cookies['remixsid6']

        if remixsid:
            self.settings['remixsid'] = remixsid

            # Нужно для авторизации в API
            self.settings['forapilogin'] = {
                'p': self.http.cookies['p'],
                'l': self.http.cookies['l']
            }

            self.sid = remixsid

        elif 'sid=' in response.url:
            captcha_sid = search_re(RE_CAPTCHAID, response.url)
            captcha = Captcha(self, captcha_sid, self.vk_login)

            if self.error_handlers[CAPTCHA_ERROR_CODE]:
                self.error_handlers[CAPTCHA_ERROR_CODE](captcha)
            else:
                raise AuthorizationError('Authorization error (capcha)')
        elif 'm=1' in response.url:
            raise BadPassword('Bad password')
        else:
            raise AuthorizationError('Unknown error. Please send bugreport.')

        if 'security_check' in response.url:
            self.security_check(response=response)

        if 'act=blocked' in response.url:
            raise AccountBlocked('Account is blocked')

    def security_check(self, url=None, response=None):
        if url:
            response = self.http.get(url)
            if 'security_check' not in response.url:
                return

        phone_prefix = search_re(RE_PHONE_PREFIX, response.text)
        if not phone_prefix:
            phone_prefix = search_re(RE_PHONE_PREFIX_2, response.text)

        phone_postfix = search_re(RE_PHONE_POSTFIX, response.text)

        if self.sec_number:
            code = self.sec_number
        elif self.number:
            code = code_from_number(phone_prefix, phone_postfix, self.number)
        elif self.login:
            code = code_from_number(phone_prefix, phone_postfix, self.login)

        if code:
            number_hash = search_re(RE_NUMBER_HASH, response.text)

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

        if phone_prefix and phone_postfix:
            raise SecurityCheck(phone_prefix, phone_postfix)
        else:
            raise SecurityCheck(response=response)

    def check_sid(self):
        """ Проверка Cookies remixsid на валидность """

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

        if 'access_token' not in response.url:
            url = search_re(RE_TOKEN_URL, response.text)
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
        """ Проверка access_token на валидность """

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

    def http_handler(self, error):
        """ Handle connection errors """
        pass

    def too_many_rps_handler(self, error):
        time.sleep(0.5)
        error.try_method()

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

        if 'v' not in values:
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

        self.last_request = time.time()
        response = self.http.post(url, values)

        if response.ok:
            response = response.json()
        else:
            error = ApiHttpError(self, method, values, response)
            response = self.http_handler(error)

            if response is not None:
                return response

            raise error

        if 'error' in response:
            error = ApiError(self, method, values, response['error'])

            if error.code in self.error_handlers:
                if error.code == CAPTCHA_ERROR_CODE:

                    error = Captcha(
                        self,
                        error.error['captcha_sid'],
                        self.method,
                        (method,),
                        {'values': values},
                        error.error['captcha_img']
                    )

                response = self.error_handlers[error.code](error)

                if response is not None:
                    return response

            raise error

        return response['response']


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


class AuthorizationError(Exception):
    pass


class BadPassword(AuthorizationError):
    pass


class AccountBlocked(AuthorizationError):
    pass


class SecurityCheck(AuthorizationError):

    def __init__(self, phone_prefix, phone_postfix, response=None):
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


class ApiError(Exception):

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


class ApiHttpError(Exception):

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
        """ Возвращает ссылку на изображение капчи

        """

        if not self.url:
            self.url = 'https://api.vk.com/captcha.php?sid={}'.format(self.sid)

        return self.url

    def try_again(self, key):
        """ Отправляет запрос заново с ответом капчи

        :param key: текст капчи
        """

        self.key = key

        self.kwargs.update({
            'captcha_sid': self.sid,
            'captcha_key': self.key
        })

        return self.func(*self.args, **self.kwargs)

    def __str__(self):
        return 'Captcha needed'
