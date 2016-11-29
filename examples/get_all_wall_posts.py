# -*- coding: utf-8 -*-

"""
@author: Seva Zhidkov
@contact: http://vk.com/shamoiseva
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2015
"""

import vk_api


def main():
    """ Пример загрузки всех постов со стены """

    login, password = 'python@vk.com', 'mypassword'

    try:
        vk = vk_api.VkApi(login, password)  # Авторизируемся
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)  # В случае ошибки выведем сообщение
        return  # и выйдем

    vk_tools = vk_api.VkTools(vk) # Создаем объект для загрузки всех элементов

    values = {
        "domain" : "id1" # Выбираем нужные параметры для метода
    }

    # Метод "get_all_slow" загружает все items или users запросами к заданному методу
    response = vk_tools.get_all_slow(method = 'wall.get', values = values)

    if response['items']:
        for post in response["items"]:
            print(post["text"])

if __name__ == '__main__':
    main()
