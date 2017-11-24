# -*- coding: utf-8 -*-
import re

from bs4 import BeautifulSoup

from .audio_url_decoder import decode_audio_url
from .exceptions import AccessDenied

RE_AUDIO = re.compile(r'audio[-\d]+_\d+_audios\d+')


class VkAudio:

    __slots__ = ('_vk', 'user_id')

    def __init__(self, vk):
        self.user_id = vk.get_api().users.get()[0]['id']
        self._vk = vk

    def get(self, owner_id=None, album_id=None, offset=0):
        """ Получить список аудиозаписей пользователя

        :param owner_id: ID владельца (отрицательные значения для групп)
        :param album_id: ID альбома (отрицательные значения для групп)
        :param offset: смещение
        """

        if owner_id is None and album_id is None:
            raise TypeError(
                'get() missing 1 required argument: album_id or owner_id'
            )
        elif owner_id is not None and album_id is not None:
            raise TypeError('get() too many arguments')

        if album_id is not None:
            url = 'https://m.vk.com/audio?act=audio_playlist{}'.format(album_id)
        else:
            url = 'https://m.vk.com/audios{}'.format(owner_id)

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

        return scrap_data(response.text, self.user_id)

    def get_albums(self, owner_id, offset=0):
        """ Получить список альбомов пользователя

        :param owner_id: ID владельца (отрицательные значения для групп)
        :param offset: смещение
        """

        response = self._vk.http.get(
            'https://m.vk.com/audio?act=audio_playlists{}'.format(owner_id),
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

        return scrap_albums(response.text)

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
            if RE_AUDIO.search(i['id'])
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
            # TODO: implement getting data of unavailable track
            continue

        artist = audio.select('.ai_artist')[0].text
        title = audio.select('.ai_title')[0].text
        duration = audio.select('.ai_dur')[0]['data-dur']
        track_id = audio['id']
        link = audio.select('.ai_body')[0].input['value']

        if 'audio_api_unavailable' in link:
            link = decode_audio_url(link, user_id)

        tracks.append({
            'artist': artist,
            'title': title,
            'dur': duration,
            'id': track_id,
            'url': link
        })

    return tracks


def scrap_albums(html):
    """ Парсинг списка альбомов из html странцы """

    soup = BeautifulSoup(html, 'html.parser')
    albums = []
    for album in soup.find_all('div', {'class': 'audioPlaylistsPage__item'}):
        link = album.select('.audioPlaylistsPage__itemLink')[0]['href']

        albums.append({
            'artist': album.select('.audioPlaylistsPage__author')[0].text,
            'title': album.select('.audioPlaylistsPage__title')[0].text,
            'plays': album.select('.audioPlaylistsPage__stats')[0].text,
            'id': album['class'][1][25:],
            'url': 'https://m.vk.com/audio?act=audio_playlist{}'.format(link)
        })

    return albums
