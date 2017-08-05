# -*- coding: utf-8 -*-
import re

from bs4 import BeautifulSoup

from .audio_url_decoder import decode_audio_url
from .exceptions import AccessDenied

RE_AUDIO = re.compile(r'audio\d+_\d+_audios\d+')


class VkAudio:

    __slots__ = ('_vk',)

    def __init__(self, vk):
        self._vk = vk

    def get(self, owner_id, offset=0):
        """ Получить список аудиозаписей пользователя

        :param owner_id: ID владельца (отрицательные значения для групп)
        :param offset: смещение
        """

        response = self._vk.http.get(
            'https://m.vk.com/audios{}'.format(owner_id),
            params={
                'offset': offset
            },
            allow_redirects=False
        )

        if not response.text:
            raise AccessDenied(
                'You don\'t have permissions to browse {}\'s audio'.format(
                    owner_id
                )
            )

        return scrap_data(response.text)

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
            i for i in scrap_data(response.text)
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

        return scrap_data(response.text)


def scrap_data(html):
    """ Парсинг списка аудиозаписей из html странцы """

    soup = BeautifulSoup(html, 'html.parser')
    tracks = []

    for audio in soup.find_all('div', {'class': 'audio_item ai_has_btn'}):
        ai_artist = audio.select('.ai_artist')
        artist = ai_artist[0].text
        link = audio.select('.ai_body')[0].input['value']

        if 'audio_api_unavailable' in link:
            link = decode_audio_url(link)

        tracks.append({
            'artist': artist,
            'title': audio.select('.ai_title')[0].text,
            'dur': audio.select('.ai_dur')[0]['data-dur'],
            'id': audio['id'],
            'url': link
        })

    return tracks
