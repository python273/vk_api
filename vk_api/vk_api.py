'''
@author: Kirill Python
@contact: http://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2013
'''

# -*- coding: utf-8 -*-
import jconfig
import re
import requests
import time


class VkApi():
    def __init__(self,
                 login=None, password=None, number=None,
                 sid=None, token=None,
                 proxies=None,
                 version='5.0', app_id=2895443, scope=2097151):
        '''
        :param login: Логин ВКонтакте
        :param password: Пароль ВКонтакте
        :param number: Номер при проверке безопасности
                        Номер: +7 12345678 90
                        number = 12345678
        :param sid: cookie remixsid
        :param token: access_token
        :param proxies: proxy server
                        {'http': 'http://127.0.0.1:8888/',
                        'https' : 'https://127.0.0.1:8888/'}
        :param version: Версия API (default: '5.0')
        :param app_id: Standalone-приложение (default: 2895443)
        :param scope: Запрашиваемые права  (default: 2097151)
        '''

        self.login = login
        self.password = password
        self.number = number

        self.sid = sid
        self.token = {'access_token': token}

        self.version = version
        self.app_id = app_id
        self.scope = scope

        self.settings = jconfig.config(login)

        self.http = requests.Session()
        self.http.proxies = proxies  # Ставим прокси
        self.http.headers = {  # Притворимся браузером
            'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) ' \
                            'Gecko/20100101 Firefox/20.0'
        }
        self.http.verify = False

        if login and password:
            self.sid = self.settings['remixsid']
            self.token = self.settings['access_token']

            if not self.check_sid():
                self.vk_login()

            if not self.check_token():
                self.api_login()

    def vk_login(self, captcha_sid=None, captcha_key=None):
        ''' Авторизцаия ВКонтакте с получением cookies remixsid '''

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
            raise authorization_error('Authorization error (capcha)')
        else:
            raise authorization_error('Authorization error (bad password)')

        if 'security_check' in response.url:
            if self.number:
                number_hash = regexp(r'security_check.*?hash: \'(.*?)\'\};',
                                     response.text)[0]

                values = {
                    'act': 'security_check',
                    'al': '1',
                    'al_page': '3',
                    'code': self.number,
                    'hash': number_hash,
                    'to': ''
                }

                response = self.http.post('https://vk.com/login.php', values)

                if response.text.split('<!>')[4] == '4':
                    return

            raise authorization_error('Authorization error (enter number)')

    def check_sid(self):
        ''' Прверка Cookies remixsid на валидность '''

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
        ''' Получение токена через Desktop приложение '''

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
            raise authorization_error('Authorization error (api)')

    def check_token(self):
        ''' Прверка access_token на валидность '''

        if self.token.get('access_token'):
            try:
                self.method('isAppUser')
            except api_error:
                return False

            return True

    def method(self, method, values=None):
        ''' Использование методов API

            method - название метода
                        'users.get'

            values - параметры
                        {'uids': 1}
        '''

        url = 'https://api.vk.com/method/%s' % method

        if not values:
            values = {}

        values.update({'v': self.version})

        if self.token:
            values.update({'access_token': self.token['access_token']})

        response = self.http.post(url, values).json()
        if 'error' in response:
            raise api_error(response['error'])
        else:
            return response['response']


def regexp(reg, string):
    ''' Поиск по регулярке '''

    reg = re.compile(reg, re.IGNORECASE | re.DOTALL)
    reg = reg.findall(string)
    return reg


class vk_api_error(Exception):
    pass


class authorization_error(vk_api_error):
    pass


class api_error(vk_api_error):
    pass
