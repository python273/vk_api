# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: https://vk.com/python273
"""

import vk_api


def main():
    """ Пример работы с VkRequestsPool """

    login, password = 'python@vk.com', 'mypassword'
    vk_session = vk_api.VkApi(login, password)

    try:
        vk_session.authorization()
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)
        return

    """
        Позволяет выполнять до 25 запросов к API за один запрос.
        Работает через метод execute.
    """

    friends = {}

    with vk_api.VkRequestsPool(vk_session) as pool:
        for user_id in [1, 183433824]:
            friends[user_id] = pool.method('friends.get', {'user_id': user_id})

    print(friends)

    # Same result
    with vk_api.VkRequestsPool(vk_session) as pool:
        friends = pool.method_one_param(
            'friends.get', key='user_id', values=[1, 183433824])

    print(friends)

    with vk_api.VkRequestsPool(vk_session) as pool:
        friends = pool.method('friends.get')
        status = pool.method('status.get')

    # Обратите внимание, что запрос выполняется после выхода из with
    # и к результатам обратиться можно только после выхода из него

    print(friends)
    print(status)

if __name__ == '__main__':
    main()
