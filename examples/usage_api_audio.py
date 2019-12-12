# -*- coding: utf-8 -*-
import requests

import vk_api
from vk_api.audio import VkAudio


""" Получение токена: """
""" 1. Установка php """
""" 2. Клонирование репозитория https://github.com/vodka2/vk-audio-token """
""" 3. Переход в vk-audio-token/src/cli """
""" 4. Получение токена: php vk-audio-token.php -m логин пароль"""
""" 5. Готово. """


def main():
    """ Использование апи аудио """

    token = 'token'
    
    session = requests.Session()
    session.headers.update({
                'User-agent': "KateMobileAndroid/52.1 lite-445 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en)"})

    vk_session = vk_api.VkApi(token=token, session=session)

    api = vk_session.get_api()
    
    search = api.audio.search(q="123") #пример поиска
    print(search)


if __name__ == '__main__':
    main()
