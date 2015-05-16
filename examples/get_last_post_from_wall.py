# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: http://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2014
"""

import vk_api


def main():
    """ Пример получения последнего сообщения со стены """

    login, password = 'python@vk.com', 'mypassword'
    vk = vk_api.VkApi(login, password)

    try:
        vk.authorization()
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)  # В случае ошибки выведем сообщение
        return  # и выйдем

    values = {
        'count': 1  # Получаем только один пост
    }
    response = vk.method('wall.get', values)  # Используем метод wall.get

    if response['items']:
        # Печатаем текст последнего поста со стены
        print(response['items'][0]['text'])

if __name__ == '__main__':
    main()
