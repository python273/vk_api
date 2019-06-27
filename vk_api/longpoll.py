# -*- coding: utf-8 -*-
"""
:authors: python273
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2019 python273
"""

from collections import defaultdict
from datetime import datetime
from enum import IntEnum

import requests
import six
from six.moves import range

CHAT_START_ID = int(2E9)  # id с которого начинаются беседы


class VkLongpollMode(IntEnum):
    """ Дополнительные опции ответа

    `Подробнее в документации VK API
    <https://vk.com/dev/using_longpoll?f=1.+Подключение>`_
    """

    #: Получать вложения
    GET_ATTACHMENTS = 2

    #: Возвращать расширенный набор событий
    GET_EXTENDED = 2**3

    #: возвращать pts для метода `messages.getLongPollHistory`
    GET_PTS = 2**5

    #: В событии с кодом 8 (друг стал онлайн) возвращать
    #: дополнительные данные в поле `extra`
    GET_EXTRA_ONLINE = 2**6

    #: Возвращать поле `random_id`
    GET_RANDOM_ID = 2**7


DEFAULT_MODE = sum(VkLongpollMode)


class VkEventType(IntEnum):
    """ Перечисление событий, получаемых от longpoll-сервера.

    `Подробнее в документации VK API
    <https://vk.com/dev/using_longpoll?f=3.+Структура+событий>`__
    """

    #: Замена флагов сообщения (FLAGS:=$flags)
    MESSAGE_FLAGS_REPLACE = 1

    #: Установка флагов сообщения (FLAGS|=$mask)
    MESSAGE_FLAGS_SET = 2

    #: Сброс флагов сообщения (FLAGS&=~$mask)
    MESSAGE_FLAGS_RESET = 3

    #: Добавление нового сообщения.
    MESSAGE_NEW = 4

    #: Редактирование сообщения.
    MESSAGE_EDIT = 5

    #: Прочтение всех входящих сообщений в $peer_id,
    #: пришедших до сообщения с $local_id.
    READ_ALL_INCOMING_MESSAGES = 6

    #: Прочтение всех исходящих сообщений в $peer_id,
    #: пришедших до сообщения с $local_id.
    READ_ALL_OUTGOING_MESSAGES = 7

    #: Друг $user_id стал онлайн. $extra не равен 0, если в mode был передан флаг 64.
    #: В младшем байте числа extra лежит идентификатор платформы
    #: (см. :class:`VkPlatform`).
    #: $timestamp — время последнего действия пользователя $user_id на сайте.
    USER_ONLINE = 8

    #: Друг $user_id стал оффлайн ($flags равен 0, если пользователь покинул сайт и 1,
    #: если оффлайн по таймауту). $timestamp — время последнего действия пользователя
    #: $user_id на сайте.
    USER_OFFLINE = 9

    #: Сброс флагов диалога $peer_id.
    #: Соответствует операции (PEER_FLAGS &= ~$flags).
    #: Только для диалогов сообществ.
    PEER_FLAGS_RESET = 10

    #: Замена флагов диалога $peer_id.
    #: Соответствует операции (PEER_FLAGS:= $flags).
    #: Только для диалогов сообществ.
    PEER_FLAGS_REPLACE = 11

    #: Установка флагов диалога $peer_id.
    #: Соответствует операции (PEER_FLAGS|= $flags).
    #: Только для диалогов сообществ.
    PEER_FLAGS_SET = 12

    #: Удаление всех сообщений в диалоге $peer_id с идентификаторами вплоть до $local_id.
    PEER_DELETE_ALL = 13

    #: Восстановление недавно удаленных сообщений в диалоге $peer_id с
    #: идентификаторами вплоть до $local_id.
    PEER_RESTORE_ALL = 14

    #: Один из параметров (состав, тема) беседы $chat_id были изменены.
    #: $self — 1 или 0 (вызваны ли изменения самим пользователем).
    CHAT_EDIT = 51

    #: Изменение информации чата $peer_id с типом $type_id
    #: $info — дополнительная информация об изменениях
    CHAT_UPDATE = 52

    #: Пользователь $user_id набирает текст в диалоге.
    #: Событие приходит раз в ~5 секунд при наборе текста. $flags = 1.
    USER_TYPING = 61

    #: Пользователь $user_id набирает текст в беседе $chat_id.
    USER_TYPING_IN_CHAT = 62

    #: Пользователь $user_id записывает голосовое сообщение в диалоге/беседе $peer_id
    USER_RECORDING_VOICE = 64

    #: Пользователь $user_id совершил звонок с идентификатором $call_id.
    USER_CALL = 70

    #: Счетчик в левом меню стал равен $count.
    MESSAGES_COUNTER_UPDATE = 80

    #: Изменились настройки оповещений.
    #: $peer_id — идентификатор чата/собеседника,
    #: $sound — 1/0, включены/выключены звуковые оповещения,
    #: $disabled_until — выключение оповещений на необходимый срок.
    NOTIFICATION_SETTINGS_UPDATE = 114


class VkPlatform(IntEnum):
    """ Идентификаторы платформ """

    #: Мобильная версия сайта или неопознанное мобильное приложение
    MOBILE = 1

    #: Официальное приложение для iPhone
    IPHONE = 2

    #: Официальное приложение для iPad
    IPAD = 3

    #: Официальное приложение для Android
    ANDROID = 4

    #: Официальное приложение для Windows Phone
    WPHONE = 5

    #: Официальное приложение для Windows 8
    WINDOWS = 6

    #: Полная версия сайта или неопознанное приложение
    WEB = 7


class VkOfflineType(IntEnum):
    """ Выход из сети в событии :attr:`VkEventType.USER_OFFLINE` """

    #: Пользователь покинул сайт
    EXIT = 0

    #: Оффлайн по таймауту
    AWAY = 1


class VkMessageFlag(IntEnum):
    """ Флаги сообщений """

    #: Сообщение не прочитано.
    UNREAD = 1

    #: Исходящее сообщение.
    OUTBOX = 2

    #: На сообщение был создан ответ.
    REPLIED = 2**2

    #: Помеченное сообщение.
    IMPORTANT = 2**3

    #: Сообщение отправлено через чат.
    CHAT = 2**4

    #: Сообщение отправлено другом.
    #: Не применяется для сообщений из групповых бесед.
    FRIENDS = 2**5

    #: Сообщение помечено как "Спам".
    SPAM = 2**6

    #: Сообщение удалено (в корзине).
    DELETED = 2**7

    #: Сообщение проверено пользователем на спам.
    FIXED = 2**8

    #: Сообщение содержит медиаконтент
    MEDIA = 2**9

    #: Приветственное сообщение от сообщества.
    HIDDEN = 2**16

    #: Сообщение удалено для всех получателей.
    DELETED_ALL = 2**17


class VkPeerFlag(IntEnum):
    """ Флаги диалогов """

    #: Важный диалог
    IMPORTANT = 1

    #: Неотвеченный диалог
    UNANSWERED = 2


class VkChatEventType(IntEnum):
    """ Идентификатор типа изменения в чате """

    #: Изменилось название беседы
    TITLE = 1

    #: Сменилась обложка беседы
    PHOTO = 2

    #: Назначен новый администратор
    ADMIN_ADDED = 3

    #: Изменены настройки беседы
    SETTINGS_CHANGED = 4

    #: Закреплено сообщение
    MESSAGE_PINNED = 5

    #: Пользователь присоединился к беседе
    USER_JOINED = 6

    #: Пользователь покинул беседу
    USER_LEFT = 7

    #: Пользователя исключили из беседы
    USER_KICKED = 8

    #: С пользователя сняты права администратора
    ADMIN_REMOVED = 9

    #: Бот прислал клавиатуру
    KEYBOARD_RECEIVED = 11


MESSAGE_EXTRA_FIELDS = [
    'peer_id', 'timestamp', 'text', 'extra_values', 'attachments', 'random_id'
]
MSGID = 'message_id'

EVENT_ATTRS_MAPPING = {
    VkEventType.MESSAGE_FLAGS_REPLACE: [MSGID, 'flags'] + MESSAGE_EXTRA_FIELDS,
    VkEventType.MESSAGE_FLAGS_SET: [MSGID, 'mask'] + MESSAGE_EXTRA_FIELDS,
    VkEventType.MESSAGE_FLAGS_RESET: [MSGID, 'mask'] + MESSAGE_EXTRA_FIELDS,
    VkEventType.MESSAGE_NEW: [MSGID, 'flags'] + MESSAGE_EXTRA_FIELDS,
    VkEventType.MESSAGE_EDIT: [MSGID, 'mask'] + MESSAGE_EXTRA_FIELDS,

    VkEventType.READ_ALL_INCOMING_MESSAGES: ['peer_id', 'local_id'],
    VkEventType.READ_ALL_OUTGOING_MESSAGES: ['peer_id', 'local_id'],

    VkEventType.USER_ONLINE: ['user_id', 'extra', 'timestamp'],
    VkEventType.USER_OFFLINE: ['user_id', 'flags', 'timestamp'],

    VkEventType.PEER_FLAGS_RESET: ['peer_id', 'mask'],
    VkEventType.PEER_FLAGS_REPLACE: ['peer_id', 'flags'],
    VkEventType.PEER_FLAGS_SET: ['peer_id', 'mask'],

    VkEventType.PEER_DELETE_ALL: ['peer_id', 'local_id'],
    VkEventType.PEER_RESTORE_ALL: ['peer_id', 'local_id'],

    VkEventType.CHAT_EDIT: ['chat_id', 'self'],
    VkEventType.CHAT_UPDATE: ['type_id', 'peer_id', 'info'],

    VkEventType.USER_TYPING: ['user_id', 'flags'],
    VkEventType.USER_TYPING_IN_CHAT: ['user_id', 'chat_id'],
    VkEventType.USER_RECORDING_VOICE: ['peer_id', 'user_id', 'flags', 'timestamp'],

    VkEventType.USER_CALL: ['user_id', 'call_id'],

    VkEventType.MESSAGES_COUNTER_UPDATE: ['count'],
    VkEventType.NOTIFICATION_SETTINGS_UPDATE: ['values']
}


def get_all_event_attrs():
    keys = set()

    for l in six.itervalues(EVENT_ATTRS_MAPPING):
        keys.update(l)

    return tuple(keys)


ALL_EVENT_ATTRS = get_all_event_attrs()

PARSE_PEER_ID_EVENTS = [
    k for k, v in six.iteritems(EVENT_ATTRS_MAPPING) if 'peer_id' in v
]
PARSE_MESSAGE_FLAGS_EVENTS = [
    VkEventType.MESSAGE_FLAGS_REPLACE,
    VkEventType.MESSAGE_NEW
]


class Event(object):
    """ Событие, полученное от longpoll-сервера.

    Имеет поля в соответствии с `документацией
    <https://vk.com/dev/using_longpoll_2?f=3.%2BСтруктура%2Bсобытий>`_.

    События `MESSAGE_NEW` и `MESSAGE_EDIT` имеют (среди прочих) такие поля:
        - `text` - `экранированный <https://ru.wikipedia.org/wiki/Мнемоники_в_HTML>`_ текст
        - `message` - оригинальный текст сообщения.

    События с полем `timestamp` также дополнительно имеют поле `datetime`.
    """

    def __init__(self, raw):
        self.raw = raw

        self.from_user = False
        self.from_chat = False
        self.from_group = False
        self.from_me = False
        self.to_me = False

        self.attachments = {}
        self.message_data = None

        self.message_id = None
        self.timestamp = None
        self.peer_id = None
        self.flags = None
        self.extra = None
        self.extra_values = None
        self.type_id = None

        try:
            self.type = VkEventType(self.raw[0])
            self._list_to_attr(self.raw[1:], EVENT_ATTRS_MAPPING[self.type])
        except ValueError:
            self.type = self.raw[0]

        if self.extra_values:
            self._dict_to_attr(self.extra_values)

        if self.type in PARSE_PEER_ID_EVENTS:
            self._parse_peer_id()

        if self.type in PARSE_MESSAGE_FLAGS_EVENTS:
            self._parse_message_flags()

        if self.type is VkEventType.CHAT_UPDATE:
            self._parse_chat_info()
            try:
                self.update_type = VkChatEventType(self.type_id)
            except ValueError:
                self.update_type = self.type_id

        elif self.type is VkEventType.NOTIFICATION_SETTINGS_UPDATE:
            self._dict_to_attr(self.values)
            self._parse_peer_id()

        elif self.type is VkEventType.PEER_FLAGS_REPLACE:
            self._parse_peer_flags()

        elif self.type in [VkEventType.MESSAGE_NEW, VkEventType.MESSAGE_EDIT]:
            self._parse_message()

        elif self.type in [VkEventType.USER_ONLINE, VkEventType.USER_OFFLINE]:
            self.user_id = abs(self.user_id)
            self._parse_online_status()

        elif self.type is VkEventType.USER_RECORDING_VOICE:
            if isinstance(self.user_id, list):
                self.user_id = self.user_id[0]

        if self.timestamp:
            self.datetime = datetime.utcfromtimestamp(self.timestamp)

    def _list_to_attr(self, raw, attrs):
        for i in range(min(len(raw), len(attrs))):
            self.__setattr__(attrs[i], raw[i])

    def _dict_to_attr(self, values):
        for k, v in six.iteritems(values):
            self.__setattr__(k, v)

    def _parse_peer_id(self):
        if self.peer_id < 0:  # Сообщение от/для группы
            self.from_group = True
            self.group_id = abs(self.peer_id)

        elif self.peer_id > CHAT_START_ID:  # Сообщение из беседы
            self.from_chat = True
            self.chat_id = self.peer_id - CHAT_START_ID

            if self.extra_values and 'from' in self.extra_values:
                self.user_id = int(self.extra_values['from'])

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
        if self.type is VkEventType.MESSAGE_NEW:
            if self.flags & VkMessageFlag.OUTBOX:
                self.from_me = True
            else:
                self.to_me = True

        # ВК возвращает сообщения в html-escaped виде,
        # при этом переводы строк закодированы как <br> и не экранированы

        self.text = self.text.replace('<br>', '\n')
        self.message = self.text \
            .replace('&lt;', '<') \
            .replace('&gt;', '>') \
            .replace('&quot;', '"') \
            .replace('&amp;', '&')

    def _parse_online_status(self):
        try:
            if self.type is VkEventType.USER_ONLINE:
                self.platform = VkPlatform(self.extra & 0xFF)

            elif self.type is VkEventType.USER_OFFLINE:
                self.offline_type = VkOfflineType(self.flags)

        except ValueError:
            pass

    def _parse_chat_info(self):
        if self.type_id == VkChatEventType.ADMIN_ADDED.value:
            self.info = {'admin_id': self.info}

        elif self.type_id == VkChatEventType.MESSAGE_PINNED.value:
            self.info = {'conversation_message_id': self.info}

        elif self.type_id in [VkChatEventType.USER_JOINED.value,
                              VkChatEventType.USER_LEFT.value,
                              VkChatEventType.USER_KICKED.value,
                              VkChatEventType.ADMIN_REMOVED.value]:
            self.info = {'user_id': self.info}


class VkLongPoll(object):
    """ Класс для работы с longpoll-сервером

    `Подробнее в документации VK API <https://vk.com/dev/using_longpoll>`__.

    :param vk: объект :class:`VkApi`
    :param wait: время ожидания
    :param mode: дополнительные опции ответа
    :param preload_messages: предзагрузка данных сообщений для
        получения ссылок на прикрепленные файлы
    :param group_id: идентификатор сообщества
        (для сообщений сообщества с ключом доступа пользователя)
    """

    __slots__ = (
        'vk', 'wait', 'mode', 'preload_messages', 'group_id',
        'url', 'session',
        'key', 'server', 'ts', 'pts'
    )

    #: Класс для событий
    DEFAULT_EVENT_CLASS = Event

    #: События, для которых можно загрузить данные сообщений из API
    PRELOAD_MESSAGE_EVENTS = [
        VkEventType.MESSAGE_NEW,
        VkEventType.MESSAGE_EDIT
    ]

    def __init__(self, vk, wait=25, mode=DEFAULT_MODE,
                 preload_messages=False, group_id=None):
        self.vk = vk
        self.wait = wait
        self.mode = mode.value if isinstance(mode, VkLongpollMode) else mode
        self.preload_messages = preload_messages
        self.group_id = group_id

        self.url = None
        self.key = None
        self.server = None
        self.ts = None
        self.pts = mode & VkLongpollMode.GET_PTS

        self.session = requests.Session()

        self.update_longpoll_server()

    def _parse_event(self, raw_event):
        return self.DEFAULT_EVENT_CLASS(raw_event)

    def update_longpoll_server(self, update_ts=True):
        values = {
            'lp_version': '3',
            'need_pts': self.pts
        }

        if self.group_id:
            values['group_id'] = self.group_id
            
        response = self.vk.method('messages.getLongPollServer', values)

        self.key = response['key']
        self.server = response['server']

        self.url = 'https://' + self.server

        if update_ts:
            self.ts = response['ts']
            if self.pts:
                self.pts = response['pts']

    def check(self):
        """ Получить события от сервера один раз

        :returns: `list` of :class:`Event`
        """
        values = {
            'act': 'a_check',
            'key': self.key,
            'ts': self.ts,
            'wait': self.wait,
            'mode': self.mode,
            'version': 3
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

            events = [
                self._parse_event(raw_event)
                for raw_event in response['updates']
            ]

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
        """ Предзагрузка данных сообщений из API

        :type events: list of Event
        """
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
        """ Слушать сервер

        :yields: :class:`Event`
        """

        while True:
            for event in self.check():
                yield event
