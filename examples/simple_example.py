# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: https://vk.com/python273
"""

import vk_api


def main():
    """ Пример получения последнего сообщения со стены """

    login, password = 'python@vk.com', 'mypassword'
    vk = vk_api.VkApi(login, password)

    try:
        vk.authorization()
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)
        return

    values = {
        'count': 1  # Получаем только один пост
    }
    response = vk.method('wall.get', values)  # Используем метод wall.get

    if response['items']:
        print(response['items'][0])

if __name__ == '__main__':
    main()
