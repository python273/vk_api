# encoding: utf-8
'''
@author: Kirill Python
@contact: https://vk.com/python273
@license Apache License, Version 2.0

Copyright (C) 2017
'''
import requests


DEFAULT_MODE = 2 + 8 + 32 + 64 + 128
CHAT_START_ID = int(2E9)  # id с которого начинаются беседы


EVENT_TYPES = {
    0: 'message_delete',
    1: 'message_flags_replace',
    2: 'message_flags_set',
    3: 'message_flags_reset',
    4: 'message_new',

    6: 'read_all_incoming_messages',
    7: 'read_all_outgoing_messages',

    8: 'user_online',
    9: 'user_offline',

    10: 'reset_filter',
    11: 'replace_filter',
    12: 'set_filter',

    51: 'chat_new',
    61: 'user_typing',
    62: 'user_typing_in_chat',

    70: 'user_call',

    80: 'messages_counter_update',
    114: 'notification_settings_update',
}

ASSOCIATIVES = {
    0: ['message_id'],
    1: ['message_id', 'flags'],
    2: ['message_id', 'mask', 'user_id'],
    3: ['message_id', 'mask', 'peer_id'],
    4: ['message_id', 'flags', 'from_id', 'timestamp', 'subject', 'text',
        'attachments'],

    6: ['peer_id', 'local_id'],
    7: ['peer_id', 'local_id'],

    8: ['user_id', 'extra'],
    9: ['user_id', 'flags'],
    10: ['peer_id', 'mask'],
    11: ['peer_id', 'flags'],
    12: ['peer_id', 'mask'],

    51: ['chat_id', 'self'],
    61: ['user_id', 'flags'],
    62: ['user_id', 'chat_id'],

    70: ['user_id', 'call_id'],
    80: ['count', 'call_id'],
    114: ['peer_id', 'sound', 'disabled_until'],
}

MESSAGE_FLAGS = [
    'unread', 'outbox', 'replied', 'important', 'chat', 'friends', 'spam',
    'deleted', 'fixed', 'media'
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
        https://new.vk.com/dev/using_longpoll_2

        :param vk: объект VkApi
        :param wait: время ожидания
        :param use_ssl: использовать шифрование
        :param mode: дополнительные опции ответа
        """
        self.vk = vk
        self.wait = wait
        self.use_ssl = use_ssl
        self.mode = mode

        self.key = None
        self.server = None
        self.ts = None
        self.pts = None

        self.update_longpoll_server()

        self.url = ('https' if use_ssl else 'http') + '://' + self.server

        self.session = requests.Session()

    def update_longpoll_server(self, update_ts=True):
        values = {
            'use_ssl': '1' if self.use_ssl else '0',
            'need_pts': '1'
        }
        response = self.vk.method('messages.getLongPollServer', values)

        self.key = response['key']
        self.server = response['server']

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
            self.url, params=values, timeout=self.wait + 10).json()

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
        'raw', 'type', 'message_flags',

        # ASSOCIATIVES
        'chat_id', 'self', 'extra', 'user_id', 'attachments', 'call_id',
        'from_id', 'subject', 'message_id', 'local_id', 'peer_id', 'timestamp',
        'flags', 'disabled_until', 'mask', 'text', 'count', 'sound',
    )

    def __init__(self, raw):
        self.raw = raw

        cmd = raw[0]

        self.type = EVENT_TYPES.get(cmd)
        self._list_to_attr(raw[1:], ASSOCIATIVES.get(cmd))

        print(self.type, ASSOCIATIVES.get(cmd))

        self.message_flags = {}

        if cmd == 4:  # New message
            self._parse_message_flags()
            self.text = self.text.replace('<br>', '\n')

            # Сообщение из чата
            if self.from_id > CHAT_START_ID:
                self.chat_id = self.from_id - CHAT_START_ID
                self.from_id = self.attachments['from']
        elif cmd == 2:
            if self.user_id > CHAT_START_ID:
                self.chat_id = self.user_id - CHAT_START_ID
                self.user_id = None
        elif cmd == 3:
            if self.peer_id > CHAT_START_ID:
                self.chat_id = self.peer_id - CHAT_START_ID
                self.peer_id = None
        elif cmd in [8, 9]:
            self.user_id = abs(self.user_id)

    def _parse_message_flags(self):
        x = 1
        for i in MESSAGE_FLAGS:

            if self.flags & x:
                self.message_flags.update({i: True})

            x *= 2

    def _list_to_attr(self, l, associative):
        if not associative:
            return

        for i in range(len(l)):
            try:
                name = associative[i]
            except IndexError:
                return True

            value = l[i]
            self.__setattr__(name, value)
