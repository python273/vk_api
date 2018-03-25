# -*- coding: utf-8 -*-
"""
@author: python273
@contact: https://vk.com/python273
@license Apache License, Version 2.0

Copyright (C) 2018
"""

import requests
import datetime
from enum import Enum


CHAT_START_ID = int(2E9)  # id с которого начинаются беседы


class VkLongpollMode(Enum):
    GET_ATTACHMENTS = 2
    GET_EXTENDED = 2**3
    GET_PTS = 2**5
    GET_EXTRA_ONLINE = 2**6
    GET_RANDOM_ID = 2**7


DEFAULT_MODE = sum([x.value for x in VkLongpollMode])


class VkEventType(Enum):
    MESSAGE_FLAGS_REPLACE = 1
    MESSAGE_FLAGS_SET = 2
    MESSAGE_FLAGS_RESET = 3
    MESSAGE_NEW = 4
    MESSAGE_EDIT = 5

    READ_ALL_INCOMING_MESSAGES = 6
    READ_ALL_OUTGOING_MESSAGES = 7

    USER_ONLINE = 8
    USER_OFFLINE = 9

    PEER_FLAGS_RESET = 10
    PEER_FLAGS_REPLACE = 11
    PEER_FLAGS_SET = 12

    PEER_DELETE_ALL = 13
    PEER_RESTORE_ALL = 14

    CHAT_EDIT = 51

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


class VkOfflineType(Enum):
    EXIT = 0
    AWAY = 1


class VkMessageFlag(Enum):
    UNREAD = 1
    OUTBOX = 2
    REPLIED = 2**2
    IMPORTANT = 2**3
    CHAT = 2**4
    FRIENDS = 2**5
    SPAM = 2**6
    DELETED = 2**7
    FIXED = 2**8
    MEDIA = 2**9
    HIDDEN = 2**16
    DELETED_ALL = 2**17


class VkPeerFlag(Enum):
    IMPORTANT = 1
    UNANSWERED = 2


MESSAGE_EXTRA_FIELDS = [
    'peer_id', 'timestamp', 'text', 'attachments', 'random_id'
]

EVENT_ATTRS_MAPPING = {
    VkEventType.MESSAGE_FLAGS_REPLACE: ['message_id', 'flags'] + MESSAGE_EXTRA_FIELDS,
    VkEventType.MESSAGE_FLAGS_SET: ['message_id', 'mask'] + MESSAGE_EXTRA_FIELDS,
    VkEventType.MESSAGE_FLAGS_RESET: ['message_id', 'mask'] + MESSAGE_EXTRA_FIELDS,
    VkEventType.MESSAGE_NEW: ['message_id', 'flags'] + MESSAGE_EXTRA_FIELDS,
    VkEventType.MESSAGE_EDIT: ['message_id', 'mask', 'peer_id', 'timestamp', 'new_text', 'attachments'],

    VkEventType.READ_ALL_INCOMING_MESSAGES: ['peer_id', 'local_id'],
    VkEventType.READ_ALL_OUTGOING_MESSAGES: ['peer_id', 'local_id'],

    VkEventType.USER_ONLINE: ['user_id', 'extra', 'timestamp'],
    VkEventType.USER_OFFLINE: ['user_id', 'extra', 'timestamp'],

    VkEventType.PEER_FLAGS_RESET: ['peer_id', 'mask'],
    VkEventType.PEER_FLAGS_REPLACE: ['peer_id', 'flags'],
    VkEventType.PEER_FLAGS_SET: ['peer_id', 'mask'],

    VkEventType.PEER_DELETE_ALL: ['peer_id', 'local_id'],
    VkEventType.PEER_RESTORE_ALL: ['peer_id', 'local_id'],

    VkEventType.CHAT_EDIT: ['chat_id', 'self'],

    VkEventType.USER_TYPING: ['user_id', 'flags'],
    VkEventType.USER_TYPING_IN_CHAT: ['user_id', 'chat_id'],

    VkEventType.USER_CALL: ['user_id', 'call_id'],

    VkEventType.MESSAGES_COUNTER_UPDATE: ['count'],
    VkEventType.NOTIFICATION_SETTINGS_UPDATE: [
        'peer_id', 'sound', 'disabled_until']
}


def get_all_event_attrs():
    keys = set()

    for l in EVENT_ATTRS_MAPPING.values():
        keys.update(l)

    return tuple(keys)


ALL_EVENT_ATTRS = get_all_event_attrs()

PARSE_PEER_ID_EVENTS = [
    k for k, v in EVENT_ATTRS_MAPPING.items() if 'peer_id' in v]


class VkLongPoll(object):

    __slots__ = (
        'vk', 'wait', 'use_ssl', 'mode',
        'url', 'session',
        'key', 'server', 'ts', 'pts'
    )

    def __init__(self, vk, wait=25, mode=DEFAULT_MODE):
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
        self.mode = mode

        self.url = None
        self.key = None
        self.server = None
        self.ts = None
        self.pts = mode & VkLongpollMode.GET_PTS.value

        self.session = requests.Session()

        self.update_longpoll_server()

    def update_longpoll_server(self, update_ts=True):
        values = {
            'lp_version': '3',
            'need_pts': self.pts
        }
        response = self.vk.method('messages.getLongPollServer', values)

        self.key = response['key']
        self.server = response['server']

        self.url = 'https://' + self.server

        if update_ts:
            self.ts = response['ts']
            if self.pts:
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
            if self.pts:
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

    __slots__ = frozenset((
        'raw', 'type', 'platform', 'offline_type',
        'user_id', 'group_id', 'peer_id',
        'flags', 'mask', 'datetime',
        'message_flags', 'peer_flags',
        'from_user', 'from_chat', 'from_group', 'from_me', 'to_me'
    )).union(ALL_EVENT_ATTRS)

    def __init__(self, raw):

        # Reset attrs to None
        for i in self.__slots__:
            self.__setattr__(i, None)

        self.raw = raw

        self.from_user = False
        self.from_chat = False
        self.from_group = False
        self.from_me = False
        self.to_me = False

        self.attachments = {}

        try:
            self.type = VkEventType(raw[0])
            self._list_to_attr(raw[1:], EVENT_ATTRS_MAPPING[self.type])
        except ValueError:
            pass

        if self.type in PARSE_PEER_ID_EVENTS:
            self._parse_peer_id()

        if self.type in [VkEventType.MESSAGE_FLAGS_REPLACE, VkEventType.MESSAGE_NEW]:
            self._parse_message_flags()

        if self.type == VkEventType.PEER_FLAGS_REPLACE:
            self._parse_peer_flags()

        if self.type == VkEventType.MESSAGE_NEW:
            self._parse_message()

        if self.type == VkEventType.MESSAGE_EDIT:
            self.new_text = self.new_text.replace('<br>', '\n')

        if self.type in [VkEventType.USER_ONLINE, VkEventType.USER_OFFLINE]:
            self.user_id = abs(self.user_id)
            self._parse_online_status()

        if self.timestamp:
            self.datetime = datetime.datetime.fromtimestamp(self.timestamp)


    def _list_to_attr(self, raw, attrs):

        for i in range(min(len(raw), len(attrs))):
            self.__setattr__(attrs[i], raw[i])

    def _parse_peer_id(self):

        if self.peer_id < 0:  # Сообщение от/для группы
            self.from_group = True
            self.group_id = abs(self.peer_id)

        elif self.peer_id > CHAT_START_ID:  # Сообщение из беседы
            self.from_chat = True
            self.chat_id = self.peer_id - CHAT_START_ID

            if 'from' in self.attachments:
                self.user_id = int(self.attachments['from'])

        else:  # Сообщение от/для пользователя
            self.from_user = True
            self.user_id = self.peer_id

    def _parse_message_flags(self):
        self.message_flags = [x for x in VkMessageFlag if self.flags & x.value]

    def _parse_peer_flags(self):
        self.peer_flags = [x for x in VkPeerFlag if self.flags & x.value]

    def _parse_message(self):

        if self.flags & VkMessageFlag.OUTBOX.value:
            self.from_me = True
        else:
            self.to_me = True

        self.text = self.text.replace('<br>', '\n')

    def _parse_online_status(self):
        try:
            if self.type == VkEventType.USER_ONLINE:
                self.platform = VkPlatform(self.extra & 0xFF)

            elif self.type == VkEventType.USER_OFFLINE:
                self.offline_type = VkOfflineType(self.flags)

        except ValueError:
            pass
