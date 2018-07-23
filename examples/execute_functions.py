# -*- coding: utf-8 -*-
""" Пример использования VkFunction - обертки над методом execute

    Описание VKScript (языка execute): https://vk.com/dev/execute
"""

import vk_api
from vk_api.execute import VkFunction


vk_add = VkFunction(args=('x', 'y'), code='''
    return %(x)s + %(y)s;
''')

vk_get_wall_post_ids = VkFunction(args=('values',), code='''
    return API.wall.get(%(values)s)["items"]@.id;
''')

vk_get_filtered = VkFunction(
    args=('method', 'values', 'key'),
    clean_args=('method', 'key'),  # аргументы будут сконвертированы через str
                                   # остальные через json.dumps
    code='''
    return API.%(method)s(%(values)s)["items"]@.%(key)s;
''')


def main():
    login, password = 'python@vk.com', 'mypassword'
    vk_session = vk_api.VkApi(login, password)

    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vk = vk_session.get_api()

    print(vk_add(vk, 2, 3))  # 5
    print(vk_add(vk, "hello ", "world!"))  # hello world!

    print(vk_get_wall_post_ids(vk, {'domain': 'python273', 'count': 100}))

    print(vk_get_filtered(vk, 'wall.get', {'domain': 'durov'}, 'text'))
    print(vk_get_filtered(vk, 'groups.get', {'extended': True}, 'name'))


if __name__ == '__main__':
    main()
