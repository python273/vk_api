# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
from .exceptions import AccessDenied


class VkAudio:
    def __init__(self, vk):
        self._vk = vk

    def get(self, owner_id, offset=0):
        """ Получение списка аудиозаписей пользователя

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
        """ Поиск по аудиозаписям пользователя

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
            
        if re.search(r'audio\d+_\d+_audios\d+', response.text):
            return [data for data in scrap_data(response.text) if not re.search(r'audio\d+_\d+_search\d+', data['id'])]

        return []
    
    def search(self, q='', offset=0):
        """ Поиск аудиозаписей

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
    """ Парсинг списка аудиозаписей """

    soup = BeautifulSoup(html, 'html.parser')
    tracks = []

    for audio in soup.find_all('div', {'class': 'audio_item ai_has_btn'}):
        ai_artist = audio.select('.ai_artist')
        artist = ai_artist[0].text
        link = audio.select('.ai_body')[0].input['value']

        tracks.append({
            'artist': artist,
            'title': audio.select('.ai_title')[0].text,
            'dur': audio.select('.ai_dur')[0]['data-dur'],
            'id': audio['id'],
            'url': link
        })

    return tracks
