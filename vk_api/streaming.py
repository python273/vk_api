# -*- coding: utf-8 -*-
"""
@author: python273, hdk5
@contact: https://vk.com/python273
@license Apache License, Version 2.0

Copyright (C) 2018
"""

from .exceptions import VkApiError
from enum import Enum
import websocket
import json


URL_TEMPLATE = "{schema}://{server}/{method}?key={key}"


class VkStreaming(object):

    __slots__ = ('vk', 'url', 'key', 'server')

    def __init__(self, vk):
        """
        :param vk: объект VkApi
        """
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
        response = self.vk.http.get(URL_TEMPLATE.format(
            schema="https",
            server=self.server,
            method="rules",
            key=self.key)
        ).json()

        if response["code"] == 200:
            return response['rules'] or []
        elif response["code"] == 400:
            raise VkStreamingError(response['error'])

    def add_rule(self, value, tag):
        response = self.vk.http.post(URL_TEMPLATE.format(
            schema="https",
            server=self.server,
            method="rules",
            key=self.key),
            json={"rule": {"value": value, "tag": tag}}
        ).json()

        if response["code"] == 200:
            return True
        elif response["code"] == 400:
            raise VkStreamingError(response['error'])

    def delete_rule(self, tag):
        response = self.vk.http.delete(URL_TEMPLATE.format(
            schema="https",
            server=self.server,
            method="rules",
            key=self.key),
            json={"tag": tag}
        ).json()

        if response["code"] == 200:
            return True
        elif response["code"] == 400:
            raise VkStreamingError(response['error'])

    def listen(self):
        ws = websocket.create_connection(URL_TEMPLATE.format(
            schema="wss",
            server=self.server,
            method="stream",
            key=self.key)
        )

        while True:
            response = ws.recv()
            response = json.loads(response)
            if response["code"] == 100:
                yield response["event"]
            elif response["code"] == 300:
                raise VkStreamingServiceMessage(response['service_message'])


class VkStreamingError(VkApiError):

    def __init__(self, error):
        self.error_code = error['error_code']
        self.message = error['message']

    def __str__(self):
        return '[{}] {}'.format(self.error_code,
                                self.message)


class VkStreamingServiceMessage(VkApiError):

    def __init__(self, error):
        self.service_code = error['service_code']
        self.message = error['message']

    def __str__(self):
        return '[{}] {}'.format(self.service_code,
                                self.message)
