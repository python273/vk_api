# encoding: utf-8

"""
@author: Kirill Python
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2017
"""

import re
import sys
import requests

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

    def get_all_audio_list(self, user_id):
        """ Отправляет id пользователя и получаем список его песен
        :param user_id: id пользователя
        """
        audio_list = []
        audio_pages_url = self.get_audio_pages(user_id)
        [audio_list.append(j) for i in list(map(self.get_audio_url, audio_pages_url))
            for j in i if j not in audio_list]
        return audio_list

    def get_audio_pages(self, user_id):
        """ Получаем список страниц
        :param user_id: id пользователя
        """
        pageuser = 'https://m.vk.com/id' + user_id
        get_user_page = requests.post(pageuser, cookies={'remixsid': self.vk.sid })
        html_user_page = get_user_page.content
        soup = BeautifulSoup(html_user_page, 'lxml')
        pos = soup.find(class_='pm_item', attrs={'href': '/audios' + user_id}).find('em', class_="pm_counter")
        num_audio = int(pos.text)
        num_pages = 1 if int((num_audio / 40)) < 1 else int((num_audio / 40))
        audio_page = 'https://m.vk.com/audio?id=' + user_id + '&offset='
        pages = [audio_page + str(int(i * 40)) for i in range(0, num_pages + 1)]
        return pages

    def get_audio_url(self, page):
        """ Отправляем страницу и получаем список всех песен на ней
        :param page: url страницы с музыкой
        """
        audio_page = requests.post(page, cookies={'remixsid': self.vk.sid})
        audio_html = audio_page.content
        soup = BeautifulSoup(audio_html, 'lxml')
        artist = soup.find_all('span', class_="ai_artist")
        title = soup.find_all('span', class_="ai_title")
        link = soup.find_all('input', type="hidden")[1:]
        regex = lambda x: re.sub(r"[\/:*?\"<>|]", "", x)
        linkreg = lambda x: re.findall('(.+\.mp3)', x)

        for a, t, l in zip(artist, title, link):
            at = regex(a.text) + ' - ' + regex(t.text)
            lin = linkreg(l.get('value'))
            yield (at, lin[0])

# Полный код в файле vk_procedures
code_get_all_items = """
var m=%s,n=%s,b="%s",v=n;var c={count:m,offset:v}+%s;var r=API.%s(c),k=r.count,
j=r[b],i=1;while(i<25&&v+m<=k){v=i*m+n;c.offset=v;j=j+API.%s(c)[b];i=i+1;}
return {count:k,items:j,offset:v+m};
""".replace('\n', '')
