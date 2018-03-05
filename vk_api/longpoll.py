# -*- coding: utf-8 -*-
"""
@author: python273
@contact: https://vk.com/python273
@license Apache License, Version 2.0

Copyright (C) 2018
"""

import requests
from enum import Enum


DEFAULT_MODE = 2 + 8 + 32 + 64 + 128
CHAT_START_ID = int(2E9)  # id с которого начинаются беседы
GROUP_START_ID = int(1E9)


class VkEventType(Enum):
    MESSAGE_DELETE = 0
    MESSAGE_FLAGS_REPLACE = 1
    MESSAGE_FLAGS_SET = 2
    MESSAGE_FLAGS_RESET = 3
    MESSAGE_NEW = 4

    READ_ALL_INCOMING_MESSAGES = 6
    READ_ALL_OUTGOING_MESSAGES = 7

    USER_ONLINE = 8
    USER_OFFLINE = 9

    PEER_FLAGS_RESET = 10
    PEER_FLAGS_REPLACE = 11
    PEER_FLAGS_SET = 12

    CHAT_NEW = 51
    USER_TYPING = 61
    USER_TYPING_IN_CHAT = 62

    USER_CALL = 70

    MESSAGES_COUNTER_UPDATE = 80
    NOTIFICATION_SETTINGS_UPDATE = 114


class VkPlatform(Enum):
    MOBILE = 1
    IPHONE = 2
    IPAD = 3
    ANDROID = 4
    WPHONE = 5
    WINDOWS = 6
    WEB = 7


class VkMessageType(Enum):
    FROM_ME = 'from_me'
    TO_ME = 'to_me'


class VkOfflineType(Enum):
    EXIT = 0
    AWAY = 1


MESSAGE_EXTRA_FIELDS = [
    'peer_id', 'timestamp', 'subject', 'text', 'attachments', 'random_id'
]

EVENT_ATTRS_MAPPING = {
    VkEventType.MESSAGE_DELETE: ['message_id'],
    VkEventType.MESSAGE_FLAGS_REPLACE: ['message_id', 'flags'] + MESSAGE_EXTRA_FIELDS,
    VkEventType.MESSAGE_FLAGS_SET: ['message_id', 'mask'] + MESSAGE_EXTRA_FIELDS,
    VkEventType.MESSAGE_FLAGS_RESET: ['message_id', 'mask'] + MESSAGE_EXTRA_FIELDS,
    VkEventType.MESSAGE_NEW: ['message_id', 'flags'] + MESSAGE_EXTRA_FIELDS,

    VkEventType.READ_ALL_INCOMING_MESSAGES: ['peer_id', 'local_id'],
    VkEventType.READ_ALL_OUTGOING_MESSAGES: ['peer_id', 'local_id'],

    VkEventType.USER_ONLINE: ['user_id', 'extra'],
    VkEventType.USER_OFFLINE: ['user_id', 'extra'],

    VkEventType.PEER_FLAGS_RESET: ['peer_id', 'mask'],
    VkEventType.PEER_FLAGS_REPLACE: ['peer_id', 'flags'],
    VkEventType.PEER_FLAGS_SET: ['peer_id', 'mask'],

    VkEventType.CHAT_NEW: ['chat_id', 'self'],
    VkEventType.USER_TYPING: ['peer_id', 'flags'],
    VkEventType.USER_TYPING_IN_CHAT: ['user_id', 'chat_id'],

    VkEventType.USER_CALL: ['user_id', 'call_id'],

    VkEventType.MESSAGES_COUNTER_UPDATE: ['count'],
    VkEventType.NOTIFICATION_SETTINGS_UPDATE: ['peer_id', 'sound', 'disabled_until'],
}


MESSAGE_FLAGS = [
    'unread', 'outbox', 'replied', 'important', 'chat', 'friends', 'spam',
    'deleted', 'fixed', 'media'
]


def get_all_event_attrs():
    keys = set()

    for l in EVENT_ATTRS_MAPPING.values():
        keys.update(l)

    return tuple(keys)


ALL_EVENT_ATTRS = get_all_event_attrs()

PARSE_PEER_ID_EVENTS = [
    VkEventType.MESSAGE_NEW,
    VkEventType.MESSAGE_FLAGS_SET,
    VkEventType.MESSAGE_FLAGS_REPLACE,
    VkEventType.READ_ALL_INCOMING_MESSAGES,
    VkEventType.READ_ALL_OUTGOING_MESSAGES,
    VkEventType.USER_TYPING
]


class VkLongPoll(object):

    __slots__ = (
        'vk', 'wait', 'use_ssl', 'mode',
        'url', 'session',
        'key', 'server', 'ts', 'pts'
    )

    def __init__(self, vk, wait=25, use_ssl=True, mode=DEFAULT_MODE):
        """
        https://vk.com/dev/using_longpoll
        https://vk.com/dev/using_longpoll_2

        :param vk: объект VkApi
        :param wait: время ожидания
        :param use_ssl: использовать шифрование
        :param mode: дополнительные опции ответа
        :param version: версия
        """
        self.vk = vk
        self.wait = wait
        self.use_ssl = use_ssl
        self.mode = mode

        self.url = None
        self.key = None
        self.server = None
        self.ts = None
        self.pts = None

        self.session = requests.Session()

        self.update_longpoll_server()

    def update_longpoll_server(self, update_ts=True):
        values = {
            'use_ssl': '1' if self.use_ssl else '0',
            'need_pts': '1'
        }
        response = self.vk.method('messages.getLongPollServer', values)

        self.key = response['key']
        self.server = response['server']

        self.url = ('https://' if self.use_ssl else 'http://') + self.server

        if update_ts:
            self.ts = response['ts']
            self.pts = response['pts']

    def check(self):
        values = {
            'act': 'a_check',
            'key': self.key,
            'ts': self.ts,
            'wait': self.wait,
            'mode': self.mode,
            'version': 1
        }

        response = self.session.get(
            self.url,
            params=values,
            timeout=self.wait + 10
        ).json()

        if 'failed' not in response:
            self.ts = response['ts']
            self.pts = response['pts']

            for raw_event in response['updates']:
                yield Event(raw_event)

        elif response['failed'] == 1:
            self.ts = response['ts']

        elif response['failed'] == 2:
            self.update_longpoll_server(update_ts=False)

        elif response['failed'] == 3:
            self.update_longpoll_server()

    def listen(self):

        while True:
            events = self.check()

            for event in events:
                yield event


class Event(object):

    __slots__ = (
        'raw', 'type', 'message_flags', 'platform', 'offline_type',
        'user_id', 'group_id',
        'from_user', 'from_chat', 'from_group', 'from_me', 'to_me'
    ) + ALL_EVENT_ATTRS

    def __init__(self, raw):

        # Reset attrs to None
        for i in self.__slots__:
            self.__setattr__(i, None)

        self.raw = raw

        self.peer_id = None
        self.from_user = False
        self.from_chat = False
        self.from_group = False
        self.from_me = False
        self.to_me = False

        self.message_flags = set()
        self.attachments = {}

        try:
            self.type = VkEventType(raw[0])
            self._list_to_attr(raw[1:], EVENT_ATTRS_MAPPING[self.type])
        except ValueError:
            pass

        if self.type in PARSE_PEER_ID_EVENTS:
            self._parse_peer_id()

            if self.type == VkEventType.MESSAGE_NEW:
                self._parse_message_flags()
                self._parse_message()

        elif self.type in [VkEventType.USER_ONLINE, VkEventType.USER_OFFLINE]:
            self.user_id = abs(self.user_id)
            self._parse_online_status()

    def _list_to_attr(self, raw, attrs):

        for i in range(min(len(raw), len(attrs))):
            self.__setattr__(attrs[i], raw[i])

    def _parse_peer_id(self):

        if self.peer_id < 0:  # Сообщение от/для группы
            self.from_group = True
            self.group_id = abs(self.peer_id)

        elif CHAT_START_ID < self.peer_id:  # Сообщение из беседы
            self.from_chat = True
            self.chat_id = self.peer_id - CHAT_START_ID

            if 'from' in self.attachments:
                self.user_id = int(self.attachments['from'])

        else:  # Сообщение от/для пользователя
            self.from_user = True
            self.user_id = self.peer_id

    def _parse_message_flags(self):
        x = 1

        for message_flag in MESSAGE_FLAGS:

            if self.flags & x:
                self.message_flags.add(message_flag)

            x *= 2

    def _parse_message(self):

        if 'outbox' in self.message_flags:
            self.from_me = True
        else:
            self.to_me = True

        self.text = self.text.replace('<br>', '\n')

    def _parse_online_status(self):
        try:
            if self.type == VkEventType.USER_ONLINE:
                self.platform = VkPlatform(self.extra & 0xFF)

            elif self.type == VkEventType.USER_OFFLINE:
                self.offline_type = VkOfflineType(self.extra)

        except ValueError:
            pass
