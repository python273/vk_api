# -*- coding: utf-8 -*-
import vk_api


def main():
    """ Пример получения всех постов со стены """

    login, password = 'python@vk.com', 'mypassword'
    vk_session = vk_api.VkApi(login, password)

    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    tools = vk_api.VkTools(vk_session)

    """ VkTools.get_all позволяет получить все объекты со всех страниц.
        Соответственно get_all используется только если метод принимает
        параметры: count и offset.

        Например может использоваться для получения всех постов стены,
        всех диалогов, всех сообщений, etc.

        При использовании get_all сокращается количество запросов к API
        за счет метода execute в 25 раз.

        Например за раз со стены можно получить 100 * 25 = 2500, где
        100 - максимальное количество постов, которое можно получить за один
        запрос (обычно написано на странице с описанием метода)
    """

    wall = tools.get_all('wall.get', 100, {'owner_id': 1})

    print('Posts count:', wall['count'])

    if wall['count']:
        print('First post:', wall['items'][0], '\n')

    if wall['count'] > 1:
        print('Last post:', wall['items'][-1])


if __name__ == '__main__':
    main()
