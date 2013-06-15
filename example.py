# -*- coding: utf-8 -*-
import vk_api

__author__ = "Kirill Python"
__email__ = "mikeking568@gmail.com"
__contact__ = "https://vk.com/python273"

""" Пример получения последнего сообщения со стены """


def main():
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
    response = vk.method('wall.get', values)  # С использованием метода wall.get
    print(response[1]['text'])  # Печатаем текст последнего поста со стены

if __name__ == '__main__':
    main()
