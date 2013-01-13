# -*- coding: utf-8 -*-
import vk_api

__author__ = "Kirill Python"
__email__ = "mikeking568@gmail.com"
__contact__ = "https://vk.com/python273"

""" Пример получения последнего сообщения со стены """


def main():
    login = u''
    password = u''

    try:
        vk = vk_api.VkApi(login, password)  # Авторизируемся
    except vk_api.authorization_error, error_msg:
        print error_msg  # В случае ошибки выведем сообщение
        return  # и выйдем

    values = {
        'count': 1  # Получаем только одно сообщение
        }
    response = vk.method('wall.get', values)  # С использованием метода wall.get
    print response[1]['text']

if __name__ == '__main__':
    main()
