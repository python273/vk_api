# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: https://vk.com/python273
"""

import vk_api


def main():
    """ Пример: загрузка фото профиля"""

    login, password = 'python@vk.com', 'mypassword'
    vk_session = vk_api.VkApi(login, password)

    try:
        vk_session.authorization()
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)
        return

    """
        В VkUpload реализованы методы загрузки файлов в ВК.
        (Не все, если что-то понадобится - могу дописать)
    """
    upload = vk_api.VkUpload(vk_session)

    photo = upload.photo_owner(  # Подставьте свои данные. Если указан только путь к изображению, то загрузка идет в
        'D:/downloads/tube.jpg', # текущий профиль пользователя.
        owner_id=-74030368
    )



    print(photo, '\nPhoto source: ', photo['photo_src'])

if __name__ == '__main__':
    main()
