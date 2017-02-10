# encoding: utf-8

"""
@author: Kirill Python
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file
Copyright (C) 2017
"""

import re
import sys

from bs4 import BeautifulSoup


if sys.version_info.major == 2:
    range = xrange


class VkAudio(object):
    """ Содержит функции для работы с VK Audio
    """

    __slots__ = ('vk',)

    def __init__(self, vk):
        """
        :param vk: объект VkApi
        """
        self.vk = vk

    def audio_get(self, owner_id = None, album_id = None, audio_ids = None, need_user = None, offset = None, count = None):
        """ Отправляет id пользователя и получаем список его песен
        :param owner_id: id пользователя
        :param album_id: идентификатор альбома с аудиозаписями.
        :param audio_ids: идентификаторы аудиозаписей, информацию о которых необходимо вернуть. список положительных чисел, разделенных запятыми
        :param need_user: 1 — возвращать информацию о пользователях, загрузивших аудиозапись. флаг, может принимать значения 1 или 0
        :param offset: смещение, необходимое для выборки определенного количества аудиозаписей. По умолчанию — 0. положительное число
        :param count: количество аудиозаписей, информацию о которых необходимо вернуть.
        """

        if owner_id is None:
            owner_id = self.vk.token['user_id']
            pageuser = 'https://m.vk.com/id' + self.vk.token['user_id']
        else:
            if owner_id[0] == '-':
                pageuser = 'https://m.vk.com/club' + owner_id[1:]
            else:
                pageuser = 'https://m.vk.com/id' + owner_id
        audio_list = []
        audio_pages_url, count = self._get_audio_pages(owner_id, pageuser)
        [audio_list.append(j) for i in list(map(self._get_audio_url, audio_pages_url))
            for j in i if j not in audio_list]
        audio_list = {
            "count": count,
            "items": audio_list
        }
        return audio_list

    def _get_audio_pages(self, user_id, pageuser):
        """ Получаем список страниц
        :param user_id: id пользователя
        """
        get_user_page = self.vk.http.post(pageuser)
        html_user_page = get_user_page.content
        soup = BeautifulSoup(html_user_page, 'html.parser')
        pos = soup.find(class_='pm_item', attrs={'href': '/audios' + user_id}).find('em', class_="pm_counter")
        num_audio = int(pos.text)
        num_pages = 1 if int((num_audio / 40)) < 1 else int((num_audio / 40))
        audio_page = 'https://m.vk.com/audio?id=' + user_id + '&offset='
        pages = [audio_page + str(int(i * 40)) for i in range(0, num_pages + 1)]
        return pages, num_audio

    def _get_audio_url(self, page):
        """ Отправляем страницу и получаем список всех песен на ней
        :param page: url страницы с музыкой
        """
        audio_page = self.vk.http.post(page)
        audio_html = audio_page.content
        soup = BeautifulSoup(audio_html, 'html.parser')
        artist = soup.find_all('span', class_="ai_artist")
        title = soup.find_all('span', class_="ai_title")
        link = soup.find_all('input', type="hidden") [1:]
        time = soup.find_all('div', class_="ai_dur")
        data = soup.find_all('div', class_="audio_item ai_has_btn")
        regex = lambda x: re.sub(r"[\/:*?\"<>|]", "", x)
        linkreg = lambda x: re.findall('(.+\.mp3)', x)
        regexid = lambda x: re.sub(r'[A-z]+', '', x)
        for a, t, l, s, d in zip(artist, title, link, time, data):
            d = d.attrs['id'].split('_')
            item = {
                "id": d[1],
                "owner_id": regexid(d[0]),
                "artist": regex(a.text),
                "title": regex(t.text),
                "url": linkreg(l.get('value'))[0],
                "duration": self._get_second(s.text),
            }
            yield item

    def _get_second(self, time):
        time = time.split(':')
        second = 0
        for key, i in enumerate(reversed(time)):
            if key == 0:
                second += int(i)
            else:
                second += 60 ** key * int(i)
        return second

# Полный код в файле vk_procedures
code_get_all_items = """
var m=%s,n=%s,b="%s",v=n;var c={count:m,offset:v}+%s;var r=API.%s(c),k=r.count,
j=r[b],i=1;while(i<25&&v+m<=k){v=i*m+n;c.offset=v;j=j+API.%s(c)[b];i=i+1;}
return {count:k,items:j,offset:v+m};
""".replace('\n', '')