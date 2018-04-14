# -*- coding: utf-8 -*-
"""
@author: python273
@contact: https://vk.com/python273
@license Apache License, Version 2.0

Copyright (C) 2018
"""

from collections import defaultdict
from datetime import datetime
from enum import Enum, IntEnum

import requests

CHAT_START_ID = int(2E9)  # id с которого начинаются беседы


class VkLongpollMode(IntEnum):
    """
    Дополнительные опции ответа

    `Подробнее в документации VK API <https://vk.com/dev/using_longpoll?f=1.+Подключение>`_
    """
    GET_ATTACHMENTS = 2
    """Получать вложения"""
    GET_EXTENDED = 2**3
    """Возвращать расширенный набор событий"""
    GET_PTS = 2**5
    """возвращать pts для метода `messages.getLongPollHistory`"""
    GET_EXTRA_ONLINE = 2**6
    """В событии с кодом 8 (друг стал онлайн) возвращать дополнительные данные в поле `extra`"""
    GET_RANDOM_ID = 2**7
    """Возвращать поле `random_id`"""


DEFAULT_MODE = sum(VkLongpollMode)


class VkEventType(IntEnum):
    """
    Перечисление событий, получаемых от longpoll-сервера.

    `Подробнее в документации VK API <https://vk.com/dev/using_longpoll?f=3.+Структура+событий>`__
    """
    MESSAGE_FLAGS_REPLACE = 1
    """Замена флагов сообщения (FLAGS:=$flags)"""
    MESSAGE_FLAGS_SET = 2
    """Установка флагов сообщения (FLAGS|=$mask)"""
    MESSAGE_FLAGS_RESET = 3
    """Сброс флагов сообщения (FLAGS&=~$mask)"""
    MESSAGE_NEW = 4
    """Добавление нового сообщения."""
    MESSAGE_EDIT = 5
    """Редактирование сообщения."""

    READ_ALL_INCOMING_MESSAGES = 6
    """Прочтение всех входящих сообщений в $peer_id, пришедших до сообщения с $local_id."""
    READ_ALL_OUTGOING_MESSAGES = 7
    """Прочтение всех исходящих сообщений в $peer_id, пришедших до сообщения с $local_id."""

    USER_ONLINE = 8
    """
    Друг $user_id стал онлайн. $extra не равен 0, если в mode был передан флаг 64.
    В младшем байте (остаток от деления на 256) числа extra лежит идентификатор
    платформы (см. :class:`VkPlatform`). $timestamp — время последнего действия
    пользователя $user_id на сайте. """
    USER_OFFLINE = 9
    """
    Друг $user_id стал оффлайн ($flags равен 0, если пользователь покинул сайт и 1,
    если оффлайн по таймауту) . $timestamp — время последнего действия пользователя
    $user_id на сайте.
    """

    PEER_FLAGS_RESET = 10
    """
    Сброс флагов диалога $peer_id.
    Соответствует операции (PEER_FLAGS &= ~$flags).
    Только для диалогов сообществ.
    """
    PEER_FLAGS_REPLACE = 11
    """
    Замена флагов диалога $peer_id.
    Соответствует операции (PEER_FLAGS:= $flags).
    Только для диалогов сообществ.
    """
    PEER_FLAGS_SET = 12
    """
    Установка флагов диалога $peer_id.
    Соответствует операции (PEER_FLAGS|= $flags).
    Только для диалогов сообществ.
    """

    PEER_DELETE_ALL = 13
    """Удаление всех сообщений в диалоге $peer_id с идентификаторами вплоть до $local_id."""
    PEER_RESTORE_ALL = 14
    """Восстановление недавно удаленных сообщений в диалоге $peer_id с идентификаторами вплоть до $local_id."""

    CHAT_EDIT = 51
    """
    Один из параметров (состав, тема) беседы $chat_id были изменены.
    $self — 1 или 0 (вызваны ли изменения самим пользователем).
    """

    USER_TYPING = 61
    """
    Пользователь $user_id набирает текст в диалоге.
    Событие приходит раз в ~5 секунд при наборе текста. $flags = 1.
    """
    USER_TYPING_IN_CHAT = 62
    """Пользователь $user_id набирает текст в беседе $chat_id."""

    USER_CALL = 70
    """Пользователь $user_id совершил звонок с идентификатором $call_id."""

    MESSAGES_COUNTER_UPDATE = 80
    """Счетчик в левом меню стал равен $count."""
    NOTIFICATION_SETTINGS_UPDATE = 114
    """Изменились настройки оповещений.
    $peer_id — идентификатор чата/собеседника,
    $sound — 1/0, включены/выключены звуковые оповещения,
    $disabled_until — выключение оповещений на необходимый срок.
    """


class VkPlatform(IntEnum):
    """Идентификаторы платформ"""
    MOBILE = 1
    """Мобильная версия сайта или неопознанное мобильное приложение"""
    IPHONE = 2
    """Официальное приложение для iPhone"""
    IPAD = 3
    """Официальное приложение для iPad"""
    ANDROID = 4
    """Официальное приложение для Android"""
    WPHONE = 5
    """Официальное приложение для Windows Phone"""
    WINDOWS = 6
    """Официальное приложение для Windows 8"""
    WEB = 7
    """Полная версия сайта или неопознанное приложение"""


class VkOfflineType(IntEnum):
    """Выход из сети в событии :attr:`VkEventType.USER_OFFLINE`"""
    EXIT = 0
    """Пользователь покинул сайт"""
    AWAY = 1
    """Оффлайн по таймауту"""


class VkMessageFlag(IntEnum):
    """Флаги сообщений"""
    UNREAD = 1
    """Cообщение не прочитано."""
    OUTBOX = 2
    """Исходящее сообщение."""
    REPLIED = 2**2
    """На сообщение был создан ответ."""
    IMPORTANT = 2**3
    """Помеченное сообщение."""
    CHAT = 2**4
    """Сообщение отправлено через чат."""
    FRIENDS = 2**5
    """
    Cообщение отправлено другом.
    Не применяется для сообщений из групповых бесед.
    """
    SPAM = 2**6
    """Cообщение помечено как "Спам"."""
    DELETED = 2**7
    """Cообщение удалено (в корзине)."""
    FIXED = 2**8
    """Cообщение проверено пользователем на спам."""
    MEDIA = 2**9
    """Cообщение содержит медиаконтент"""
    HIDDEN = 2**16
    """Приветственное сообщение от сообщества."""
    DELETED_ALL = 2**17
    """Cообщение удалено для всех получателей."""


class VkPeerFlag(IntEnum):
    """Флаги диалогов"""
    IMPORTANT = 1
    """Важный диалог"""
    UNANSWERED = 2
    """Неотвеченный диалог"""


MESSAGE_EXTRA_FIELDS = [
    'peer_id', 'timestamp', 'subject', 'text', 'attachments', 'random_id'
]

EVENT_ATTRS_MAPPING = {
    VkEventType.MESSAGE_FLAGS_REPLACE: ['message_id', 'flags'] + MESSAGE_EXTRA_FIELDS,
    VkEventType.MESSAGE_FLAGS_SET: ['message_id', 'mask'] + MESSAGE_EXTRA_FIELDS,
    VkEventType.MESSAGE_FLAGS_RESET: ['message_id', 'mask'] + MESSAGE_EXTRA_FIELDS,
    VkEventType.MESSAGE_NEW: ['message_id', 'flags'] + MESSAGE_EXTRA_FIELDS,
    VkEventType.MESSAGE_EDIT: ['message_id', 'mask'] + MESSAGE_EXTRA_FIELDS,

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
    k for k, v in EVENT_ATTRS_MAPPING.items() if 'peer_id' in v
]
PARSE_MESSAGE_FLAGS_EVENTS = [
    VkEventType.MESSAGE_FLAGS_REPLACE,
    VkEventType.MESSAGE_NEW
]


class VkLongPoll(object):
    """
    Класс для работы с longpoll-сервером

    `Подробнее в документации VK API <https://vk.com/dev/using_longpoll>`__.

    :param vk: объект :class:`VkApi`
    :param wait: время ожидания
    :param mode: дополнительные опции ответа
    :param preload_messages: предзагрузка данных сообщений для
        получения ссылок на прикрепленные файлы
    """

    __slots__ = (
        'vk', 'wait', 'mode', 'preload_messages',
        'url', 'session',
        'key', 'server', 'ts', 'pts'
    )

    PRELOAD_MESSAGE_EVENTS = [
        VkEventType.MESSAGE_NEW,
        VkEventType.MESSAGE_EDIT
    ]

    def __init__(self, vk, wait=25, mode=DEFAULT_MODE, preload_messages=False):
        self.vk = vk
        self.wait = wait
        self.mode = mode
        self.preload_messages = preload_messages

        self.url = None
        self.key = None
        self.server = None
        self.ts = None
        self.pts = mode & VkLongpollMode.GET_PTS

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
        """
        Получить события от сервера один раз

        :returns: `list` of :class:`Event`
        """
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

            events = [Event(raw_event) for raw_event in response['updates']]

            if self.preload_messages:
                self.preload_message_events_data(events)

            return events

        elif response['failed'] == 1:
            self.ts = response['ts']

        elif response['failed'] == 2:
            self.update_longpoll_server(update_ts=False)

        elif response['failed'] == 3:
            self.update_longpoll_server()

        return []

    def preload_message_events_data(self, events):
        message_ids = set()
        event_by_message_id = defaultdict(list)

        for event in events:
            if event.type in self.PRELOAD_MESSAGE_EVENTS:
                message_ids.add(event.message_id)
                event_by_message_id[event.message_id].append(event)

        if not message_ids:
            return

        messages_data = self.vk.method(
            'messages.getById',
            {'message_ids': message_ids}
        )

        for message in messages_data['items']:
            for event in event_by_message_id[message['id']]:
                event.message_data = message

    def listen(self):
        """
        Слушать сервер

        :yields: :class:`Event`
        """

        while True:
            for event in self.check():
                yield event


class Event(object):
    """
    Событие, полученное от longpoll-сервера. 

    Имеет поля в соответствии с `документацией <https://vk.com/dev/using_longpoll?f=3.%20Структура%20событий>`_.

    События с полем `timestamp` также дополнительно имеют поле `datetime`
    """

    __slots__ = frozenset((
        'raw', 'type', 'platform', 'offline_type',
        'user_id', 'group_id', 'peer_id',
        'flags', 'mask', 'datetime',
        'message_flags', 'peer_flags',
        'from_user', 'from_chat', 'from_group', 'from_me', 'to_me',
        'message_data'
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
        self.message_data = None

        try:
            self.type = VkEventType(raw[0])
            self._list_to_attr(raw[1:], EVENT_ATTRS_MAPPING[self.type])
        except ValueError:
            pass

        if self.type in PARSE_PEER_ID_EVENTS:
            self._parse_peer_id()

        if self.type in PARSE_MESSAGE_FLAGS_EVENTS:
            self._parse_message_flags()

        if self.type is VkEventType.PEER_FLAGS_REPLACE:
            self._parse_peer_flags()

        if self.type is VkEventType.MESSAGE_NEW:
            self._parse_message()

        if self.type is VkEventType.MESSAGE_EDIT:
            self.text = self.text.replace('<br>', '\n')

        if self.type in [VkEventType.USER_ONLINE, VkEventType.USER_OFFLINE]:
            self.user_id = abs(self.user_id)
            self._parse_online_status()

        if self.timestamp:
            self.datetime = datetime.utcfromtimestamp(self.timestamp)

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
        self.message_flags = set(
            x for x in VkMessageFlag if self.flags & x
        )

    def _parse_peer_flags(self):
        self.peer_flags = set(
            x for x in VkPeerFlag if self.flags & x
        )

    def _parse_message(self):

        if self.flags & VkMessageFlag.OUTBOX:
            self.from_me = True
        else:
            self.to_me = True

        self.text = self.text.replace('<br>', '\n')

    def _parse_online_status(self):
        try:
            if self.type is VkEventType.USER_ONLINE:
                self.platform = VkPlatform(self.extra & 0xFF)

            elif self.type is VkEventType.USER_OFFLINE:
                self.offline_type = VkOfflineType(self.flags)

        except ValueError:
            pass
