# -*- coding: utf-8 -*-
import requests
from jconfig import config
import re

cj_from_dict = requests.utils.cookiejar_from_dict


class VkApi():
    def __init__(self, login=None, password=None, sid=None, token=None,
                    auth_in_api=True, app_id=2895443, scope=2097151,
                    proxies={}):

        self.login = login
        self.password = password
        self.sid = sid
        self.token = {'access_token': token}
        self.settings = config(login)

        self.app_id = app_id
        self.scope = scope

        self.http = requests.Session()
        self.http.proxies = proxies  # Ставим прокси если есть
        self.http.headers = {  # Притворимся браузером
            'User-agent': 'Opera/9.80 (Windows NT 6.1; WOW64; U; ru) Presto/2.10.289 Version/12.00'
            }
        self.http.verify = False  # Сертификаты не будем проверять

        if login and password:  # Oh...
            self.sid = self.settings['remixsid']
            self.token = self.settings['access_token']

            if not self.check_sid():
                if not self.vk_login():
                    raise authorization_error('Authorization error (bad password)')
            if auth_in_api:
                if not self.check_token():
                    if not self.api_login():
                        raise authorization_error('Authorization error (api)')

    def vk_login(self, captcha_sid='', captcha_key=''):
        """ Авторизцаия ВКонтакте с получением cookies remixsid """

        url = 'http://login.vk.com/'
        data = {
            'act': 'login',
            'utf8': '1',
            'captcha_sid': captcha_sid,
            'captcha_key': captcha_key,
            'email': self.login,
            'pass': self.password
            }

        if 'remixsid' in self.http.cookies:
            self.http.cookies.pop('remixsid')
        response = self.http.post(url, data)

        if 'remixsid' in self.http.cookies:
            remixsid = self.http.cookies['remixsid']
            self.settings['remixsid'] = remixsid

            # Нужно в авторизации через api_login
            self.settings['forapilogin'] = {
                'p': self.http.cookies['p'],
                'l': self.http.cookies['l']
                }

            self.sid = remixsid
            return True
        elif 'sid=' in response.url:
            raise authorization_error('Authorization error (capcha)')

    def check_sid(self):
        """ Прверка Cookies remixsid на валидность """

        if self.sid:
            url = 'https://vk.com/feed2.php'
            self.http.cookies = cj_from_dict({
                'remixsid': self.sid,
                'remixlang': '0',
                'remixsslsid': '1'
                })

            response = self.http.post(url).json()

            if response['user']['id'] != -1:
                return response

    def api_login(self):
        """ Получение токена через Desktop приложение """

        url = 'https://oauth.vk.com/authorize'
        data = {
            'client_id': self.app_id,
            'scope': self.scope,
            'response_type': 'token',
            }

        cookies = {}
        cookies.update(self.settings['forapilogin'])
        cookies.update({'remixsid': self.sid})
        cookies = cj_from_dict(cookies)
        self.http.cookies = cookies

        response = self.http.post(url, data)

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
            return True

    def check_token(self):
        """ Прверка access_token на валидность """

        if self.token.get('access_token'):
            try:
                self.method('isAppUser')
            except:
                return False

            return True

    def method(self, method, data={}):
        """ Использование методов API """

        url = 'https://api.vk.com/method/%s' % (method)
        data.update({'access_token': self.token['access_token']})

        response = self.http.post(url, data).json()
        if 'error' in response:
            raise api_error(response['error'])
        else:
            return response['response']


def regexp(reg, string):
    """ Поиск по регулярке """

    reg = re.compile(reg, re.IGNORECASE | re.DOTALL)
    reg = reg.findall(string)
    return reg


class vk_api_error(Exception):
    pass


class authorization_error(vk_api_error):
    pass


class api_error(vk_api_error):
    pass
