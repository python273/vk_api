from bs4 import BeautifulSoup
import re
from .exceptions import AccessRightsError

RE_VALUE = re.compile(r'>(.*?)<')
RE_DURATION = re.compile(r'data-dur="([0-9]*)"')


class VKAudio:
    def __init__(self, vk):
        self._vk = vk

    def get(self, **kwargs):
        response = self._vk.http.get('https://m.vk.com/audios{}'.format(kwargs['owner_id']),
                                     params={'offset': kwargs.get('offset', 0)},
                                     allow_redirects=False)

        if response.text == '':
            raise AccessRightsError("You dont have permissions to browse {}'s audios".format(kwargs['owner_id']))

        return scrap_data(response.text)

    def search(self, **kwargs):
        response = self._vk.http.get('https://m.vk.com/audio', params={'act': 'search',
                                                                       'q': kwargs['q'],
                                                                       'offset': kwargs.get('offset', 0)})
        return scrap_data(response.text)


def value(tag, duration=False):
    string = str(tag)
    if duration:
        regex = RE_DURATION
    else:
        regex = RE_VALUE
    extracted = regex.search(string)
    if extracted:
        groups = extracted.groups()
        return groups[0]
    return None


def scrap_data(html):
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
