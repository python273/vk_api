"""
:authors: python273, kyzima-spb
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2019 python273
"""

import json
import re
import typing as t

import requests

from .exceptions import AuthError
from .utils import (
    set_cookies_from_list,
    generate_device_id,
    search_re,
)


__all__ = (
    'WebLoginCredentials',
)


class WebLoginCredentials:
    """
    Парсит и хранит данные новой формы входа,
    нужные для процесса аутентификации и авторизации пользователя.
    """

    SIGNIN_URL = 'https://m.vk.com/join?vkid_auth_type=sign_in'
    DEFAULT_COOKIES = [
        {  # если не установлено, то не будет редирект на страницу с данными аутентификации
            'version': 0,
            'name': 'remixmdevice',
            'value': '1920/1080/2/!!-!!!!',
            'port': None,
            'port_specified': False,
            'domain': '.vk.com',
            'domain_specified': True,
            'domain_initial_dot': True,
            'path': '/',
            'path_specified': True,
            'secure': True,
            'expires': None,
            'discard': False,
            'comment': None,
            'comment_url': None,
            'rfc2109': False,
            'rest': {}
        }
    ]

    def __init__(
        self,
        session: requests.Session,
        api_version: str = '5.207',
    ) -> None:
        set_cookies_from_list(session.cookies, self.DEFAULT_COOKIES)

        response = session.get(self.SIGNIN_URL)
        pattern = re.compile(r'window\.init\s*=\s*({.*?});', re.DOTALL)
        json_config = search_re(pattern, response.text)

        if json_config is None:
            raise AuthError('Failed to get the value of variable window.init.')

        self._config = json.loads(json_config)

        self.sid = ''
        self.can_skip_password = False

        self.device_id = generate_device_id()
        self.api_version = api_version

    @property
    def app_id(self) -> str:
        """ID приложения, через которое выполняется вход."""
        return self._config['auth']['host_app_id']

    @property
    def uuid(self) -> str:
        """
        Уникальный идентификатор запроса.

        (вероятно, временный для конкретного входа).
        """
        return self._config['data']['uuid']

    @property
    def access_token(self) -> str:
        """Токен доступа."""
        return self._config['auth']['access_token']

    @property
    def anonymous_token(self) -> str:
        """Анонимный токен доступа."""
        return self._config['auth']['anonymous_token']
