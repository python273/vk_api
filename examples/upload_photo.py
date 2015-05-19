# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: https://vk.com/python273
"""

import vk_api


def main():
    """ Пример: загрузка фото """

    login, password = 'python@vk.com', 'mypassword'
    vk = vk_api.VkApi(login, password)

    try:
        vk.authorization()
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)
        return

    upload = vk_api.VkUpload(vk)
    photo = upload.photo(  # Подставте свои данные
        'D:/downloads/tube.jpg',
        album_id=200851098,
        group_id=74030368
    )

    vk_url = 'https://vk.com/photo{}_{}'.format(
        photo[0]['owner_id'], photo[0]['id']
    )

    print(photo, '\nLink: ', vk_url)

if __name__ == '__main__':
    main()
