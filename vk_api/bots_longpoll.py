import requests

CHAT_START_ID = int(2E9)
MESSAGE_EVENT_TYPES = [
    'message_new',
    'message_reply',
    'message_edit'
]


class VkBotsLongPoll(object):
    __slots__ = (
        'vk', 'wait', 'preload_messages',
        'url', 'session',
        'key', 'server', 'ts'
    )

    def __init__(self, vk, group_id, wait=25):
        self.vk = vk
        self.group_id = group_id
        self.wait = wait

        self.url = None
        self.key = None
        self.server = None
        self.ts = None

        self.session = requests.Session()

        self.update_longpoll_server()

    def update_longpoll_server(self, update_ts=True):
        values = {
            'group_id': self.group_id
        }
        response = self.vk.method('groups.getLongPollServer', values)

        self.key = response['key']
        self.server = response['server']

        self.url = 'https://' + self.server

        if update_ts:
            self.ts = response['ts']

    def check(self):
        values = {
            'act': 'a_check',
            'key': self.key,
            'ts': self.ts,
            'wait': self.wait,
        }

        response = self.session.get(
            self.url,
            params=values,
            timeout=self.wait + 10
        ).json()

        if 'failed' not in response:
            self.ts = response['ts']
            events = [BotEvent(raw_event) for raw_event in response['updates']]
            return events

        elif response['failed'] == 1:
            self.ts = response['ts']

        elif response['failed'] == 2:
            self.update_longpoll_server(update_ts=False)

        elif response['failed'] == 3:
            self.update_longpoll_server()

        return []

    def listen(self):
        while True:
            for event in self.check():
                yield event


class BotEvent(object):
    __slots__ = frozenset((
        'raw', 'type', 'object',
        'id', 'date', 'peer_id',
        'from_id', 'text'
    ))

    def __init__(self, raw):

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
            self.type = raw['type']
            self.object = raw['object']
        except ValueError:
            pass

        if self.type in MESSAGE_EVENT_TYPES:
            self._parse_message()

    def _parse_message(self):
        for k, w in self.object.items():
            self.__setattr__(k, w)

        if self.type == 'message_new':
            self.to_me = True
        else:
            self.from_me = True

        if self.peer_id < 0:
            self.from_group = True
        elif self.peer_id < CHAT_START_ID:
            self.from_user = True
        else:
            self.from_chat = True
