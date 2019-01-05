# -*- coding: utf-8 -*-
from vk_api import vk_api


def main():
    """ Пример получения access_token из сode после OAuth авторизации на сайте
    """

    code = '18dczc1337a63427fa'
    redirect_url = 'http://example.com'
    app = 000000
    secret = 'dGbpoJdqNuMlGDECgO9I'

    vk_session = vk_api.VkApi(app_id=app, client_secret=secret)

    try:
        vk_session.code_auth(code, redirect_url)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    print(vk_session.token['user_id'])
    print(vk_session.token['access_token'])


if __name__ == '__main__':
    main()
