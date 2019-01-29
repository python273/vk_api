# -*- coding: utf-8 -*-
"""
:authors: python273, hdk5
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2019 python273
"""

from .exceptions import VkApiError
import websocket
import json


class VkStreaming(object):
    """ Класс для работы с Streaming API

    `Подробнее в документации VK API <https://vk.com/dev/streaming_api_docs>`__.

    :param vk: объект :class:`VkApi`
    """

    __slots__ = ('vk', 'url', 'key', 'server')

    URL_TEMPLATE = '{schema}://{server}/{method}?key={key}'

    def __init__(self, vk):
        self.vk = vk

        self.url = None
        self.key = None
        self.server = None

        self.update_streaming_server()

    def update_streaming_server(self):
        response = self.vk.method('streaming.getServerUrl')

        self.key = response['key']
        self.server = response['endpoint']

    def get_rules(self):
        """ Получить список добавленных правил """
        response = self.vk.http.get(self.URL_TEMPLATE.format(
            schema='https',
            server=self.server,
            method='rules',
            key=self.key)
        ).json()

        if response['code'] == 200:
            return response['rules'] or []
        elif response['code'] == 400:
            raise VkStreamingError(response['error'])

    def add_rule(self, value, tag):
        """ Добавить правило

        :param value: Строковое представление правила
        :type value: str

        :param tag: Тег правила
        :type tag: str
        """
        response = self.vk.http.post(self.URL_TEMPLATE.format(
            schema='https',
            server=self.server,
            method='rules',
            key=self.key),
            json={'rule': {'value': value, 'tag': tag}}
        ).json()

        if response['code'] == 200:
            return True
        elif response['code'] == 400:
            raise VkStreamingError(response['error'])

    def delete_rule(self, tag):
        """ Удалить правило

        :param tag: Тег правила
        :type tag: str
        """
        response = self.vk.http.delete(self.URL_TEMPLATE.format(
            schema='https',
            server=self.server,
            method='rules',
            key=self.key),
            json={'tag': tag}
        ).json()

        if response['code'] == 200:
            return True
        elif response['code'] == 400:
            raise VkStreamingError(response['error'])

    def listen(self):
        """ Слушать сервер """
        ws = websocket.create_connection(self.URL_TEMPLATE.format(
            schema='wss',
            server=self.server,
            method='stream',
            key=self.key
        ))

        while True:
            response = json.loads(ws.recv())

            if response['code'] == 100:
                yield response['event']
            elif response['code'] == 300:
                raise VkStreamingServiceMessage(response['service_message'])


class VkStreamingError(VkApiError):

    def __init__(self, error):
        self.error_code = error['error_code']
        self.message = error['message']

    def __str__(self):
        return '[{}] {}'.format(self.error_code, self.message)


class VkStreamingServiceMessage(VkApiError):

    def __init__(self, error):
        self.service_code = error['service_code']
        self.message = error['message']

    def __str__(self):
        return '[{}] {}'.format(self.service_code, self.message)
