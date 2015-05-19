# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: https://vk.com/python273
"""

import vk_api


def main():
    """ Пример: получение всех постов со стены """

    login, password = 'python@vk.com', 'mypassword'
    vk = vk_api.VkApi(login, password)

    try:
        vk.authorization()
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)
        return

    tools = vk_api.VkTools(vk)

    wall = tools.get_all('wall.get', 100, {'owner_id': '183433824'})
    print('Posts count:', wall['count'])

    if wall['count']:
        print('First post:', wall['items'][0], '\n')

    if wall['count'] > 1:
        print('Last post:', wall['items'][-1])

if __name__ == '__main__':
    main()
