from bs4 import BeautifulSoup
import re
from .exceptions import AccessDenied

RE_VALUE = re.compile(r'>(.*?)<')
RE_DURATION = re.compile(r'data-dur="([0-9]*)"')


class VKAudio:
    def __init__(self, vk):
        self._vk = vk

    def get(self, owner_id, offset=0):
        """ Получение html со списком аудиозаписей пользователя"""
        response = self._vk.http.get(
            'https://m.vk.com/audios{}'.format(owner_id),
            params={'offset': offset},
            allow_redirects=False)

        if response.text == '':
            raise AccessDenied("You dont have permissions to browse {}'s audios".format(kwargs['owner_id']))
        return scrap_data(response.text)

    def search(self, q='', offset=0):
        """ Получение html со списком аудиозаписей по запросу """
        response = self._vk.http.get(
            'https://m.vk.com/audio',
            params={'act': 'search',
                    'q': q,
                    'offset': offset})
        return scrap_data(response.text)


def value(tag, duration=False):
    """ Извлечение значений из html тега """
    if duration:
        return tag[0]['data-dur']
    return tag[0].text


def scrap_data(html):
    """ Сбор информации из html и записывание ее в словарь """
    soup = BeautifulSoup(html, "html.parser")
    songs = []

    for audio in soup.find_all("div", {"class": "audio_item ai_has_btn"}):
        ai_artist = audio.select('.ai_artist')
        artist = ai_artist[0].text
        data = {'artist': artist,
                'title': value(audio.select('.ai_title')),
                'dur': value(audio.select('.ai_dur'), duration=True),
                'id': audio['id']}
        songs.append(data)
    return songs
