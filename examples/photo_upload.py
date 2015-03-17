# -*- coding: utf-8 -*-

"""
@author: Seva Zhidkov
@contact: http://vk.com/shamoiseva
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2015
"""

import vk_api


def main():
    """ Пример загрузки фотографии в альбом """

    login, password = 'python@vk.com', 'mypassword'

    try:
        vk = vk_api.VkApi(login, password)  # Авторизируемся
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)  # В случае ошибки выведем сообщение
        return  # и выйдем

    vk_upload = vk_api.VkApi(vk) # Создаем объект для загрузки фото

    album_id = 205431099 # Выбираем ID альбома

    response = vk_upload.photo(photos = ["img1.png", "img2.png"], # Метод "photo" добавляет фотографию в альбом
                               album_id = album_id)

    if response['items']:
        for photo in response["items"]:
            print("Добавлена фотография с ID ", photo["id"]) # ID каждой фотографии выводим

if __name__ == '__main__':
    main()
