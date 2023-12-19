# -*- coding: utf-8 -*-
"""
:authors: python273
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2019 python273
"""

import json
import logging
import random
import re
import threading
import time
import urllib.parse
from hashlib import md5

import requests

import jconfig
from .enums import VkUserPermissions
from .exceptions import *
from .utils import (
    code_from_number, search_re, clear_string,
    cookies_to_list, set_cookies_from_list
)

RE_LOGIN_TO = re.compile(r'"to":"(.*?)"')
RE_LOGIN_IP_H = re.compile(r'name="ip_h" value="([a-z0-9]+)"')
RE_LOGIN_LG_H = re.compile(r'name="lg_h" value="([a-z0-9]+)"')
RE_LOGIN_LG_DOMAIN_H = re.compile(r'name="lg_domain_h" value="([a-z0-9]+)"')

RE_CAPTCHAID = re.compile(r"onLoginCaptcha\('(\d+)'")
RE_NUMBER_HASH = re.compile(r"al_page: '3', hash: '([a-z0-9]+)'")
RE_AUTH_HASH = re.compile(r"Authcheck\.init\('([a-z_0-9]+)'")
RE_TOKEN_URL = re.compile(r'location\.href = "(.*?)"\+addr;')
RE_AUTH_TOKEN_URL = re.compile(r'window\.init = ({.*?});')

RE_PHONE_PREFIX = re.compile(r'label ta_r">\+(.*?)<')
RE_PHONE_POSTFIX = re.compile(r'phone_postfix">.*?(\d+).*?<')

DEFAULT_USERAGENT = 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'

DEFAULT_USER_SCOPE = sum(VkUserPermissions)


def get_unknown_exc_str(s):
    return (
        f'Unknown error ({s}). Please send a bugreport to GitHub: '
        'https://github.com/python273/vk_api/issues'
    )


class VkApi(object):
    """
    :param login: Логин ВКонтакте (лучше использовать номер телефона для
        автоматического обхода проверки безопасности)
    :type login: str

    :param password: Пароль ВКонтакте (если пароль не передан, то будет
        попытка использовать сохраненные данные)
    :type password: str

    :param token: access_token
    :type token: str

    :param auth_handler: Функция для обработки двухфакторной аутентификации,
        должна возвращать строку с кодом и
        булево значение, означающее, стоит ли запомнить
        это устройство, для прохождения аутентификации.
    :param captcha_handler: Функция для обработки капчи, см. :func:`captcha_handler`
    :param config: Класс для сохранения настроек
    :type config: :class:`jconfig.base.BaseConfig`
    :param config_filename: Расположение config файла для :class:`jconfig.config.Config`

    :param api_version: Версия API
    :type api_version: str

    :param app_id: app_id Standalone-приложения
    :type app_id: int

    :param scope: Запрашиваемые права, можно передать строкой или числом.
        См. :class:`VkUserPermissions`
    :type scope: int or str

    :param client_secret: Защищенный ключ приложения для Client Credentials Flow
        авторизации приложения (https://vk.com/dev/client_cred_flow).
        Внимание: Этот способ авторизации устарел, рекомендуется использовать
        сервисный ключ из настроек приложения.


    `login` и `password` необходимы для автоматического получения токена при помощи
    Implicit Flow авторизации пользователя и возможности работы с веб-версией сайта
    (включая :class:`vk_api.audio.VkAudio`)

    :param session: Кастомная сессия со своими параметрами(из библиотеки requests)
    :type session: :class:`requests.Session`
    """

    RPS_DELAY = 0.34  # ~3 requests per second

    def __init__(self, login=None, password=None, token=None,
                 auth_handler=None, captcha_handler=None,
                 config=jconfig.Config, config_filename='vk_config.v2.json',
                 api_version='5.92', app_id=6222115, scope=DEFAULT_USER_SCOPE,
                 client_secret=None, session=None):

        self.login = login
        self.password = password

        self.token = {'access_token': token}

        self.api_version = api_version
        self.app_id = app_id
        self.scope = scope
        self.client_secret = client_secret

        self.storage = config(self.login, filename=config_filename)

        self.http = session or requests.Session()
        if not session:
            self.http.headers['User-agent'] = DEFAULT_USERAGENT

        self.last_request = 0.0

        self.error_handlers = {
            NEED_VALIDATION_CODE: self.need_validation_handler,
            CAPTCHA_ERROR_CODE: captcha_handler or self.captcha_handler,
            TOO_MANY_RPS_CODE: self.too_many_rps_handler,
            TWOFACTOR_CODE: auth_handler or self.auth_handler
        }

        self.lock = threading.Lock()

        self.logger = logging.getLogger('vk_api')

    @property
    def _sid(self):
        return (
            self.http.cookies.get('remixsid', domain='.vk.com') or
            self.http.cookies.get('remixsid6', domain='.vk.com') or
            self.http.cookies.get('remixsid', domain='.vk.ru') or
            self.http.cookies.get('remixsid6', domain='.vk.ru')
        )

    def auth(self, reauth=False, token_only=False):
        """ Аутентификация

        :param reauth: Позволяет переавторизоваться, игнорируя сохраненные
            куки и токен

        :param token_only: Включает оптимальную стратегию аутентификации, если
            необходим только access_token

            Например если сохраненные куки не валидны,
            но токен валиден, то аутентификация пройдет успешно

            При token_only=False, сначала проверяется
            валидность куки. Если кука не будет валидна, то
            будет произведена попытка аутетификации с паролем.
            Тогда если пароль не верен или пароль не передан,
            то аутентификация закончится с ошибкой.

            Если вы не делаете запросы к веб версии сайта
            используя куки, то лучше использовать
            token_only=True
        """

        if not self.login:
            raise LoginRequired('Login is required to auth')

        self.logger.info(f'Auth with login: {self.login}')

        set_cookies_from_list(
            self.http.cookies,
            self.storage.setdefault('cookies', [])
        )

        self.token = (
            self.storage.setdefault('token', {})
            .setdefault(f'app{str(self.app_id)}', {})
            .get(f'scope_{str(self.scope)}')
        )

        if token_only:
            self._auth_token(reauth=reauth)
        else:
            self._auth_cookies(reauth=reauth)

    def _auth_cookies(self, reauth=False):

        if reauth:
            self.logger.info('Auth forced')

            self.storage.clear_section()

            self._vk_login()
            self._api_login()
            return

        if not self.check_sid():
            self.logger.info(f'remixsid from config is not valid: {self._sid}')

            self._vk_login()
        else:
            self._pass_security_check()

        if not self._check_token():
            self.logger.info(f'access_token from config is not valid: {self.token}')

            self._api_login()
        else:
            self.logger.info('access_token from config is valid')

    def _auth_token(self, reauth=False):

        if not reauth and self._check_token():
            self.logger.info('access_token from config is valid')
            return

        if reauth:
            self.logger.info('Auth (API) forced')

        if self.check_sid():
            self._pass_security_check()
            self._api_login()

        elif self.password:
            self._vk_login()
            self._api_login()

    def _vk_login(self, captcha_sid=None, captcha_key=None):
        """ Авторизация ВКонтакте с получением cookies remixsid

        :param captcha_sid: id капчи
        :type captcha_key: int or str

        :param captcha_key: ответ капчи
        :type captcha_key: str
        """

        self.logger.info('Logging in...')

        if not self.password:
            raise PasswordRequired('Password is required to login')

        self.http.cookies.clear()

        # Get cookies
        response = self.http.get('https://vk.com/login')

        if response.url.startswith('https://vk.com/429.html?'):
            hash429_md5 = md5(self.http.cookies['hash429'].encode('ascii')).hexdigest()
            self.http.cookies.pop('hash429')
            response = self.http.get(f'{response.url}&key={hash429_md5}')

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://vk.com/',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://vk.com',
        }

        values = {
            'act': 'login',
            'role': 'al_frame',
            'expire': '',
            'to': search_re(RE_LOGIN_TO, response.text),
            'recaptcha': '',
            'captcha_sid': '',
            'captcha_key': '',
            '_origin': 'https://vk.com',
            'utf8': '1',
            'ip_h': search_re(RE_LOGIN_IP_H, response.text),
            'lg_h': search_re(RE_LOGIN_LG_H, response.text),
            'lg_domain_h': search_re(RE_LOGIN_LG_DOMAIN_H, response.text),
            'ul': '',
            'email': self.login,
            'pass': self.password
        }

        if captcha_sid and captcha_key:
            self.logger.info(f'Using captcha code: {captcha_sid}: {captcha_key}')
            values['captcha_sid'] = captcha_sid
            values['captcha_key'] = captcha_key

        response = self.http.post(
            'https://login.vk.com/?act=login',
            data=values,
            headers=headers
        )

        if 'onLoginCaptcha(' in response.text:
            self.logger.info('Captcha code is required')

            captcha_sid = search_re(RE_CAPTCHAID, response.text)
            captcha = Captcha(self, captcha_sid, self._vk_login)

            return self.error_handlers[CAPTCHA_ERROR_CODE](captcha)

        if 'onLoginReCaptcha(' in response.text:
            self.logger.info('Captcha code is required (recaptcha)')

            captcha_sid = str(random.random())[2:16]
            captcha = Captcha(self, captcha_sid, self._vk_login)

            return self.error_handlers[CAPTCHA_ERROR_CODE](captcha)

        if 'onLoginFailed(4' in response.text:
            raise BadPassword('Bad password')

        if 'act=authcheck' in response.text:
            self.logger.info('2FA is required')

            response = self.http.get('https://vk.com/login?act=authcheck')

            self._pass_twofactor(response)

        if not self._sid:
            raise AuthError(get_unknown_exc_str('AUTH; no sid'))

        self.logger.info('Got remixsid')

        self.storage.cookies = cookies_to_list(self.http.cookies)
        self.storage.save()
        response = self._pass_security_check(response)

        if 'act=blocked' in response.url:
            raise AccountBlocked('Account is blocked')

    def _pass_twofactor(self, auth_response, captcha_sid=None, captcha_key=None):
        """ Двухфакторная аутентификация

        :param auth_response: страница с приглашением к аутентификации
        """

        auth_hash = search_re(RE_AUTH_HASH, auth_response.text)

        if not auth_hash:
            raise TwoFactorError(get_unknown_exc_str('2FA; no hash'))

        code, remember_device = self.error_handlers[TWOFACTOR_CODE]()

        values = {
            'al': '1',
            'code': code,
            'hash': auth_hash,
            'remember': int(remember_device),
        }
        if captcha_sid and captcha_key:
            self.logger.info(f'Using captcha code: {captcha_sid}: {captcha_key}')
            values['captcha_sid'] = captcha_sid
            values['captcha_key'] = captcha_key

        response = self.http.post(
            'https://vk.com/al_login.php?act=a_authcheck_code',
            values
        )
        data = json.loads(response.text.lstrip('<!--'))
        status = data['payload'][0]

        if status == '4':  # OK
            path = json.loads(data['payload'][1][0])
            return self.http.get(path)

        elif status in [0, '8']:  # Incorrect code
            return self._pass_twofactor(auth_response)

        elif status == '2':
            if data['payload'][1][1] != 2:
                # Regular captcha
                self.logger.info('Captcha code is required')

                captcha_sid = data['payload'][1][0][1:-1]
                captcha = Captcha(self, captcha_sid, self._pass_twofactor, (auth_response,))

                return self.error_handlers[CAPTCHA_ERROR_CODE](captcha)
            raise TwoFactorError('Recaptcha required')

        raise TwoFactorError(get_unknown_exc_str('2FA; unknown status'))

    def _pass_security_check(self, response=None):
        """ Функция для обхода проверки безопасности (запрос номера телефона)

        :param response: ответ предыдущего запроса, если есть
        """

        self.logger.info('Checking security check request')

        if response is None:
            response = self.http.get('https://vk.com/settings')

        if 'security_check' not in response.url:
            self.logger.info('Security check is not required')
            return response

        phone_prefix = clear_string(search_re(RE_PHONE_PREFIX, response.text))
        phone_postfix = clear_string(
            search_re(RE_PHONE_POSTFIX, response.text))

        code = None
        if self.login and phone_prefix and phone_postfix:
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
                return response

        if phone_prefix and phone_postfix:
            raise SecurityCheck(phone_prefix, phone_postfix)

        raise SecurityCheck(response=response)

    def check_sid(self):
        """ Проверка Cookies remixsid на валидность """

        self.logger.info('Checking remixsid...')

        if not self._sid:
            self.logger.info('No remixsid')
            return

        feed_url = 'https://vk.com/feed.php'
        response = self.http.get(feed_url)

        if response.url != feed_url:
            self.logger.info('remixsid is not valid')
            return False

        self.logger.info('remixsid is valid')
        return True

    def _api_login(self):
        """ Получение токена через Desktop приложение """

        if not self._sid:
            raise AuthError('API auth error (no remixsid)')

        if not self.http.cookies.get('p', domain='.login.vk.com'):
            raise AuthError('API auth error (no login cookies)')

        response = self.http.get(
            'https://oauth.vk.com/authorize',
            params={
                'client_id': self.app_id,
                'scope': self.scope,
                'response_type': 'token'
            }
        )

        if 'act=blocked' in response.url:
            raise AccountBlocked('Account is blocked')

        if 'access_token' not in response.url:
            url = search_re(RE_TOKEN_URL, response.text)
            if url:
                response = self.http.get(url)
            elif 'redirect_uri' in response.url:
                response = self.http.get(response.url)
                auth_json = json.loads(search_re(RE_AUTH_TOKEN_URL, response.text))
                return_auth_hash = auth_json['data']['hash']['return_auth']
                response = self.http.post(
                    'https://login.vk.com/?act=connect_internal',
                    {
                        'uuid': '',
                        'service_group': '',
                        'return_auth_hash': return_auth_hash,
                        'version': 1,
                        'app_id': self.app_id,
                    },
                    headers={'Origin': 'https://id.vk.com'}
                )
                connect_data = response.json()
                if connect_data['type'] != 'okay':
                    raise AuthError('Unknown API auth error')
                auth_token = connect_data['data']['access_token']
                response = self.http.post(
                    'https://api.vk.com/method/auth.getOauthToken',
                    {
                        'hash': return_auth_hash,
                        'app_id': self.app_id,
                        'client_id': self.app_id,
                        'scope': self.scope,
                        'access_token': auth_token,
                        'is_seamless_auth': 1,
                        'v': '5.207'
                    }
                )

                self.token = response.json()['response']

                self.storage.setdefault('token', {}).setdefault(
                    f'app{str(self.app_id)}', {}
                )[f'scope_{str(self.scope)}'] = self.token

                self.storage.save()

                self.logger.info('Got access_token')
                return


        if 'access_token' in response.url:
            parsed_url = urllib.parse.urlparse(response.url)
            parsed_query = urllib.parse.parse_qs(parsed_url.query)

            if 'authorize_url' in parsed_query:
                url = parsed_query['authorize_url'][0]

                if url.startswith('https%3A'):  # double-encoded
                    url = urllib.parse.unquote(url)

                parsed_url = urllib.parse.urlparse(url)

            parsed_query = urllib.parse.parse_qs(parsed_url.fragment)

            token = {k: v[0] for k, v in parsed_query.items()}

            if not isinstance(token.get('access_token'), str):
                raise AuthError(get_unknown_exc_str('API AUTH; no access_token'))

            self.token = token

            self.storage.setdefault('token', {}).setdefault(
                f'app{str(self.app_id)}', {}
            )[f'scope_{str(self.scope)}'] = token

            self.storage.save()

            self.logger.info('Got access_token')

        elif 'oauth.vk.com/error' in response.url:
            error_data = response.json()

            error_text = error_data.get('error_description')

            # Deletes confusing error text
            if error_text and '@vk.com' in error_text:
                error_text = error_data.get('error')

            raise AuthError(f'API auth error: {error_text}')

        else:
            raise AuthError('Unknown API auth error')

    def server_auth(self):
        """ Серверная авторизация """
        values = {
            'client_id': self.app_id,
            'client_secret': self.client_secret,
            'v': self.api_version,
            'grant_type': 'client_credentials'
        }

        response = self.http.post(
            'https://oauth.vk.com/access_token', values
        ).json()

        if 'error' in response:
            raise AuthError(response['error_description'])
        else:
            self.token = response

    def code_auth(self, code, redirect_url):
        """ Получение access_token из code """
        values = {
            'client_id': self.app_id,
            'client_secret': self.client_secret,
            'v': self.api_version,
            'redirect_uri': redirect_url,
            'code': code,
        }

        response = self.http.post(
            'https://oauth.vk.com/access_token', values
        ).json()

        if 'error' in response:
            raise AuthError(response['error_description'])
        else:
            self.token = response
        return response

    def _check_token(self):
        """ Проверка access_token юзера на валидность """

        if self.token:
            try:
                self.method('stats.trackVisitor')
            except ApiError:
                return False

            return True

    def captcha_handler(self, captcha):
        """ Обработчик капчи (http://vk.com/dev/captcha_error)

        :param captcha: объект исключения `Captcha`
        """

        raise captcha

    def need_validation_handler(self, error):
        """ Обработчик проверки безопасности при запросе API
            (http://vk.com/dev/need_validation)

        :param error: исключение
        """

        pass  # TODO: write me

    def http_handler(self, error):
        """ Обработчик ошибок соединения

        :param error: исключение
        """

        pass

    def too_many_rps_handler(self, error):
        """ Обработчик ошибки "Слишком много запросов в секунду".
            Ждет полсекунды и пробует отправить запрос заново

        :param error: исключение
        """

        self.logger.warning('Too many requests! Sleeping 0.5 sec...')

        time.sleep(0.5)
        return error.try_method()

    def auth_handler(self):
        """ Обработчик двухфакторной аутентификации """

        raise AuthError('No handler for two-factor authentication')

    def get_api(self):
        """ Возвращает VkApiMethod(self)

            Позволяет обращаться к методам API как к обычным классам.
            Например vk.wall.get(...)
        """

        return VkApiMethod(self)

    def method(self, method, values=None, captcha_sid=None, captcha_key=None,
               raw=False):
        """ Вызов метода API

        :param method: название метода
        :type method: str

        :param values: параметры
        :type values: dict

        :param captcha_sid: id капчи
        :type captcha_key: int or str

        :param captcha_key: ответ капчи
        :type captcha_key: str

        :param raw: при False возвращает `response['response']`
                    при True возвращает `response`
                    (может понадобиться для метода execute для получения
                    execute_errors)
        :type raw: bool
        """

        values = values.copy() if values else {}

        if 'v' not in values:
            values['v'] = self.api_version

        if self.token:
            values['access_token'] = self.token['access_token']

        if captcha_sid and captcha_key:
            values['captcha_sid'] = captcha_sid
            values['captcha_key'] = captcha_key

        with self.lock:
            # Ограничение 3 запроса в секунду
            delay = self.RPS_DELAY - (time.time() - self.last_request)

            if delay > 0:
                time.sleep(delay)

            response = self.http.post(
                f'https://api.vk.com/method/{method}',
                values,
                headers={'Cookie': ''},
            )
            self.last_request = time.time()

        if response.ok:
            response = response.json()
        else:
            error = ApiHttpError(self, method, values, raw, response)
            response = self.http_handler(error)

            if response is not None:
                return response

            raise error

        if 'error' in response:
            error = ApiError(self, method, values, raw, response['error'])

            if error.code in self.error_handlers:
                if error.code == CAPTCHA_ERROR_CODE:
                    error = Captcha(
                        self,
                        error.error['captcha_sid'],
                        self.method,
                        (method,),
                        {'values': values, 'raw': raw},
                        error.error['captcha_img']
                    )

                response = self.error_handlers[error.code](error)

                if response is not None:
                    return response

            raise error

        return response if raw else response['response']

class VkApiGroup(VkApi):
    """Предназначен для авторизации с токеном группы.
    Увеличивает частоту обращений к API с 3 до 20 в секунду.
    """
    RPS_DELAY = 1 / 20.0

class VkApiMethod(object):
    """ Дает возможность обращаться к методам API через:

    >>> vk = VkApiMethod(...)
    >>> vk.wall.getById(posts='...')
    или
    >>> vk.wall.get_by_id(posts='...')
    """

    __slots__ = ('_vk', '_method')

    def __init__(self, vk, method=None):
        self._vk = vk
        self._method = method

    def __getattr__(self, method):
        if '_' in method:
            m = method.split('_')
            method = m[0] + ''.join(i.title() for i in m[1:])

        return VkApiMethod(
            self._vk, (f'{self._method}.' if self._method else '') + method
        )

    def __call__(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, (list, tuple)):
                kwargs[k] = ','.join(str(x) for x in v)

        return self._vk.method(self._method, kwargs)
