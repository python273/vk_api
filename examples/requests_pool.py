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
        TODO: write description
    """

    friends = {}

    with vk_api.VkRequestsPool(vk_session) as pool:
        for user_id in [1, 183433824]:
            friends[user_id] = pool.method('friends.get', {'user_id': user_id})

    print(friends)

    with vk_api.VkRequestsPool(vk_session) as pool:
        friends = pool.method('friends.get')
        status = pool.method('status.get')

    print(friends)
    print(status)

if __name__ == '__main__':
    main()
