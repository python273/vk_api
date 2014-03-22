# -*- coding: utf-8 -*-
'''
@author: Kirill Python
@contact: http://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2013
'''


import vk_api


def main():
    u""" Пример получения последнего сообщения со стены """

    login = u'python@vk.com'
    password = u'mypassword'

    try:
        vk = vk_api.VkApi(login, password)  # Авторизируемся
    except vk_api.authorization_error as error_msg:
        print(error_msg)  # В случае ошибки выведем сообщение
        return  # и выйдем

    values = {
        'count': 1  # Получаем только одно сообщение
    }
    response = vk.method('wall.get', values)  # Используем метод wall.get
    print(response[1]['text'])  # Печатаем текст последнего поста со стены

if __name__ == '__main__':
    main()
