# -*- coding: utf-8 -*-
"""
:authors: python273
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2019 python273
"""

import re
import json
import time
from itertools import islice

from bs4 import BeautifulSoup

from .audio_url_decoder import decode_audio_url
from .exceptions import AccessDenied
from .utils import set_cookies_from_list

RE_ALBUM_ID = re.compile(r'act=audio_playlist(-?\d+)_(\d+)')
RE_ACCESS_HASH = re.compile(r'access_hash=(\w+)')
RE_M3U8_TO_MP3 = re.compile(r'/[0-9a-f]+(/audios)?/([0-9a-f]+)/index.m3u8')
RPS_DELAY = 1.5

TRACKS_PER_USER_PAGE = 50
TRACKS_PER_ALBUM_PAGE = 100
ALBUMS_PER_USER_PAGE = 100


class VkAudio(object):
    """ Модуль для получения аудиозаписей без использования официального API.

    :param vk: Объект :class:`VkApi`
    """

    __slots__ = ('_vk', 'user_id', 'convert_m3u8_links')

    DEFAULT_COOKIES = [
        {  # если не установлено, то первый запрос ломается
            'version': 0,
            'name': 'remixaudio_show_alert_today',
            'value': '0',
            'port': None,
            'port_specified': False,
            'domain': '.vk.com',
            'domain_specified': True,
            'domain_initial_dot': True,
            'path': '/',
            'path_specified': True,
            'secure': True,
            'expires': None,
            'discard': False,
            'comment': None,
            'comment_url': None,
            'rfc2109': False,
            'rest': {}
        }, {  # для аудио из постов
            'version': 0,
            'name': 'remixmdevice',
            'value': '1920/1080/2/!!-!!!!',
            'port': None,
            'port_specified': False,
            'domain': '.vk.com',
            'domain_specified': True,
            'domain_initial_dot': True,
            'path': '/',
            'path_specified': True,
            'secure': True,
            'expires': None,
            'discard': False,
            'comment': None,
            'comment_url': None,
            'rfc2109': False,
            'rest': {}
        }
    ]

    def __init__(self, vk, convert_m3u8_links=True):
        self.user_id = vk.method('users.get')[0]['id']
        self._vk = vk
        self.convert_m3u8_links = convert_m3u8_links

        set_cookies_from_list(self._vk.http.cookies, self.DEFAULT_COOKIES)

        self._vk.http.get('https://m.vk.com/')  # load cookies

    def get_iter(self, owner_id=None, album_id=None, access_hash=None):
        """ Получить список аудиозаписей пользователя (по частям)

        :param owner_id: ID владельца (отрицательные значения для групп)
        :param album_id: ID альбома
        :param access_hash: ACCESS_HASH альбома
        """

        if owner_id is None:
            owner_id = self.user_id

        if album_id is not None:
            url = 'https://m.vk.com/audio?act=audio_playlist{}_{}&access_hash={}'.format(
                owner_id, album_id, access_hash or ''
            )
            offset_diff = TRACKS_PER_ALBUM_PAGE
        else:
            url = 'https://m.vk.com/audios{}'.format(owner_id)
            offset_diff = TRACKS_PER_USER_PAGE

        offset = 0
        while True:
            response = self._vk.http.get(
                url,
                params={
                    'offset': offset
                },
                allow_redirects=False
            )

            if not response.text:
                raise AccessDenied(
                    'You don\'t have permissions to browse user\'s audio'
                )

            tracks = scrap_data(
                response.text,
                self.user_id,
                filter_root_el={'class_': 'audioPlaylist__list'} if album_id else None,
                convert_m3u8_links=self.convert_m3u8_links,
                http=self._vk.http
            )

            if not tracks:
                break

            for i in tracks:
                yield i

            offset += offset_diff

    def get(self, owner_id=None, album_id=None, access_hash=None):
        """ Получить список аудиозаписей пользователя

        :param owner_id: ID владельца (отрицательные значения для групп)
        :param album_id: ID альбома
        :param access_hash: ACCESS_HASH альбома
        """

        return list(self.get_iter(owner_id, album_id, access_hash))

    def get_albums_iter(self, owner_id=None):
        """ Получить список альбомов пользователя (по частям)

        :param owner_id: ID владельца (отрицательные значения для групп)
        """

        if owner_id is None:
            owner_id = self.user_id

        offset = 0

        while True:
            response = self._vk.http.get(
                'https://m.vk.com/audio?act=audio_playlists{}'.format(
                    owner_id
                ),
                params={
                    'offset': offset
                },
                allow_redirects=False
            )

            if not response.text:
                raise AccessDenied(
                    'You don\'t have permissions to browse {}\'s albums'.format(
                        owner_id
                    )
                )

            albums = scrap_albums(response.text)

            if not albums:
                break

            for i in albums:
                yield i

            offset += ALBUMS_PER_USER_PAGE

    def get_albums(self, owner_id=None):
        """ Получить список альбомов пользователя

        :param owner_id: ID владельца (отрицательные значения для групп)
        """

        return list(self.get_albums_iter(owner_id))

    def search_user(self, owner_id=None, q=''):
        """ Искать по аудиозаписям пользователя

        :param owner_id: ID владельца (отрицательные значения для групп)
        :param q: запрос
        """

        if owner_id is None:
            owner_id = self.user_id

        response = self._vk.http.get(
            'https://m.vk.com/audio',
            params={
                'id': owner_id,
                'q': q
            },
            allow_redirects=False
        )

        if not response.text:
            raise AccessDenied(
                'You don\'t have permissions to browse {}\'s audio'.format(
                    owner_id
                )
            )

        tracks = scrap_data(
            response.text,
            self.user_id,
            filter_root_el={'class_': 'AudioSerp__found'},
            convert_m3u8_links=self.convert_m3u8_links,
            http=self._vk.http
        )

        return [track for track in tracks if track['owner_id'] == owner_id]

    def search(self, q, count=50):
        """ Искать аудиозаписи

        :param q: запрос
        :param count: количество
        """

        return islice(self.search_iter(q), count)

    def search_iter(self, q, offset=0):
        """ Искать аудиозаписи (генератор)

        :param q: запрос
        :param offset: смещение
        """

        while True:
            response = self._vk.http.get(
                'https://m.vk.com/audio',
                params={
                    'act': 'search',
                    'q': q,
                    'offset': offset
                }
            )

            tracks = scrap_data(
                response.text,
                self.user_id,
                convert_m3u8_links=self.convert_m3u8_links,
                http=self._vk.http
            )

            if not tracks:
                break

            for track in tracks:
                yield track

            offset += 50

    def get_audio_by_id(self, owner_id, audio_id):
        """ Получить аудиозапись по ID

        :param owner_id: ID владельца (отрицательные значения для групп)
        :param audio_id: ID аудио
        """
        response = self._vk.http.get(
            'https://m.vk.com/audio{}_{}'.format(owner_id, audio_id),
            allow_redirects=False
        )
        track = scrap_data(
            response.text,
            self.user_id,
            filter_root_el={'class': 'basisDefault'},
            convert_m3u8_links=self.convert_m3u8_links,
            http=self._vk.http
        )
        if track:
            return track[0]['url']
        else:
            return ''

    def get_post_audio(self, owner_id, post_id):
        """ Получить список аудиозаписей из поста пользователя или группы

        :param owner_id: ID владельца (отрицательные значения для групп)
        :param post_id: ID поста
        """
        response = self._vk.http.get(
            'https://m.vk.com/wall{}_{}'.format(owner_id, post_id)
        )

        tracks = scrap_data(
            response.text,
            self.user_id,
            filter_root_el={'class': 'audios_list'},
            convert_m3u8_links=self.convert_m3u8_links,
            http=self._vk.http
        )

        return tracks


def scrap_data(html, user_id, filter_root_el=None, convert_m3u8_links=True, http=None):
    """ Парсинг списка аудиозаписей из html страницы """

    if filter_root_el is None:
        filter_root_el = {'id': 'au_search_items'}

    soup = BeautifulSoup(html, 'html.parser')
    tracks = []
    ids = []

    last_request = 0.0

    root_el = soup.find(**filter_root_el)

    if root_el is None:
        raise ValueError('Could not find root el for audio')

    playlist_snippets = soup.find_all('div', {'class': "audioPlaylistSnippet__list"})
    for playlist in playlist_snippets:
        playlist.decompose()

    for audio in root_el.find_all('div', {'class': 'audio_item'}):
        if 'audio_item_disabled' in audio['class']:
            continue

        data_audio = json.loads(audio['data-audio'])
        data_audio[13] = re.sub('(/+)', '/', data_audio[13].strip('/')).split('/')
        if len(data_audio[13]) == 6:
            data_audio[13] = [data_audio[13][2], data_audio[13][4]]
        else:
            data_audio[13] = data_audio[13][-2:]

        full_id = (
            str(data_audio[1]), str(data_audio[0]), data_audio[13][0], data_audio[13][1]
        )
        ids.append(full_id)

    for ids_group in [ids[i:i + 10] for i in range(0, len(ids), 10)]:
        delay = RPS_DELAY - (time.time() - last_request)

        if delay > 0:
            time.sleep(delay)

        result = http.post(
            'https://m.vk.com/audio',
            data={'act': 'reload_audio', 'ids': ','.join(['_'.join(i) for i in ids_group])}
        ).json()

        last_request = time.time()
        if result['data']:
            data_audio = result['data'][0]
            for audio in data_audio:
                artist = BeautifulSoup(audio[4], 'html.parser').text
                title = BeautifulSoup(audio[3].strip(), 'html.parser').text
                duration = audio[5]
                link = audio[2]

                if 'audio_api_unavailable' in link:
                    link = decode_audio_url(link, user_id)

                if convert_m3u8_links and 'm3u8' in link:
                    link = RE_M3U8_TO_MP3.sub(r'\1/\2.mp3', link)

                tracks.append({
                    'id': audio[0],
                    'owner_id': audio[1],
                    'track_covers': audio[14].split(',') if audio[14] else '',
                    'url': link,

                    'artist': artist,
                    'title': title,
                    'duration': duration,
                })

    return tracks


def scrap_albums(html):
    """ Парсинг списка альбомов из html страницы """

    soup = BeautifulSoup(html, 'html.parser')
    albums = []

    for album in soup.find_all('div', {'class': 'audioPlaylistsPage__item'}):

        link = album.select_one('.audioPlaylistsPage__itemLink')['href']
        full_id = tuple(int(i) for i in RE_ALBUM_ID.search(link).groups())
        access_hash = RE_ACCESS_HASH.search(link)

        stats_text = album.select_one('.audioPlaylistsPage__stats').text

        # "1 011 прослушиваний"
        try:
            plays = int(stats_text.rsplit(' ', 1)[0].replace(' ', ''))
        except ValueError:
            plays = None

        albums.append({
            'id': full_id[1],
            'owner_id': full_id[0],
            'url': 'https://m.vk.com/audio?act=audio_playlist{}_{}'.format(
                *full_id
            ),
            'access_hash': access_hash.group(1) if access_hash else None,

            'title': album.select_one('.audioPlaylistsPage__title').text,
            'plays': plays
        })

    return albums
