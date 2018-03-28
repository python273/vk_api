# -*- coding: utf-8 -*-
import re

from bs4 import BeautifulSoup

from .audio_url_decoder import decode_audio_url
from .exceptions import AccessDenied

RE_AUDIO_ID = re.compile(r'audio(-?\d+)_(\d+)')
RE_ALBUM_ID = re.compile(r'act=audio_playlist(-?\d+)_(\d+)')

TRACKS_PER_USER_PAGE = 50
TRACKS_PER_ALBUM_PAGE = 100
ALBUMS_PER_USER_PAGE = 100


class VkAudio(object):

    __slots__ = ('_vk', 'user_id')

    def __init__(self, vk):
        self.user_id = vk.method('users.get')[0]['id']
        self._vk = vk

    def get_iter(self, owner_id, album_id=None):
        """ Получить список аудиозаписей пользователя (по частям)

        :param owner_id: ID владельца (отрицательные значения для групп)
        :param album_id: ID альбома
        """

        if album_id is not None:
            url = 'https://m.vk.com/audio?act=audio_playlist{}_{}'.format(
                owner_id, album_id
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

            tracks = scrap_data(response.text, self.user_id)

            if not tracks:
                break

            for i in tracks:
                yield i

            offset += offset_diff

    def get(self, owner_id, album_id=None):
        """ Получить список аудиозаписей пользователя

        :param owner_id: ID владельца (отрицательные значения для групп)
        :param album_id: ID альбома
        """

        return list(self.get_iter(owner_id, album_id))

    def get_albums_iter(self, owner_id):
        """ Получить список альбомов пользователя (по частям)

        :param owner_id: ID владельца (отрицательные значения для групп)
        """

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

    def get_albums(self, owner_id):
        """ Получить список альбомов пользователя

        :param owner_id: ID владельца (отрицательные значения для групп)
        """

        return list(self.get_albums_iter(owner_id))

    def search_user(self, owner_id, q=''):
        """ Искать по аудиозаписям пользователя

        :param owner_id: ID владельца (отрицательные значения для групп)
        :param q: запрос
        """

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

        return [
            i for i in scrap_data(response.text, self.user_id)
            if i['owner_id'] == owner_id
        ]

    def search(self, q='', offset=0):
        """ Искать аудиозаписи

        :param q: запрос
        :param offset: смещение
        """

        response = self._vk.http.get(
            'https://m.vk.com/audio',
            params={
                'act': 'search',
                'q': q,
                'offset': offset
            }
        )

        return scrap_data(response.text, self.user_id)


def scrap_data(html, user_id):
    """ Парсинг списка аудиозаписей из html странцы """

    soup = BeautifulSoup(html, 'html.parser')
    tracks = []
    for audio in soup.find_all('div', {'class': 'audio_item'}):
        if 'audio_item_disabled' in audio["class"]:
            continue

        artist = audio.select('.ai_artist')[0].text
        title = audio.select('.ai_title')[0].text
        duration = audio.select('.ai_dur')[0]['data-dur']
        duration = int(duration)
        full_id = tuple(int(i) for i in RE_AUDIO_ID.findall(audio['id'])[0])
        link = audio.select('.ai_body')[0].input['value']

        if 'audio_api_unavailable' in link:
            link = decode_audio_url(link, user_id)

        tracks.append({
            'artist': artist,
            'title': title,
            'duration': duration,
            'id': full_id[1],
            'owner_id': full_id[0],
            'url': link
        })

    return tracks


def scrap_albums(html):
    """ Парсинг списка альбомов из html странцы """

    soup = BeautifulSoup(html, 'html.parser')
    albums = []
    for album in soup.find_all('div', {'class': 'audioPlaylistsPage__item'}):
        link = album.select('.audioPlaylistsPage__itemLink')[0]['href']
        full_id = tuple(int(i) for i in RE_ALBUM_ID.findall(link)[0])

        albums.append({
            'title': album.select('.audioPlaylistsPage__title')[0].text,
            'plays': int(album.select('.audioPlaylistsPage__stats')[0].text.split()[0]),
            'id': full_id[1],
            'owner_id': full_id[0],
            'url': 'https://m.vk.com/audio?act=audio_playlist{}_{}'.format(
                *full_id
            )
        })

    return albums
