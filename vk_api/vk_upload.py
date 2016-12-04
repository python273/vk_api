# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2016
"""


class VkUpload(object):
    def __init__(self, vk):
        """

        :param vk: объект VkApi
        """

        self.vk = vk
        # https://vk.com/dev/upload_files

    def photo(self, photos, album_id,
              latitude=None, longitude=None, caption=None, description=None,
              group_id=None):
        """ Загрузка изображений в альбом пользователя

        :param photos: список путей к изображениям, либо путь к изображению
        :param album_id: идентификатор альбома
        :param latitude: географическая широта, заданная в градусах
                            (от -90 до 90)
        :param longitude: географическая долгота, заданная в градусах
                            (от -180 до 180)
        :param caption: текст описания изображения
        :param description: текст описания альбома
        :param group_id: идентификатор сообщества (если загрузка идет в группу)
        """

        values = {'album_id': album_id}

        if group_id:
            values['group_id'] = group_id

        # Получаем ссылку для загрузки
        url = self.vk.method('photos.getUploadServer', values)['upload_url']

        # Загружаем
        photos_files = open_files(photos)
        response = self.vk.http.post(url, files=photos_files).json()
        close_files(photos_files)

        # Олег Илларионов:
        # это не могу к сожалению просто пофиксить
        if 'album_id' not in response:
            response['album_id'] = response['aid']

        response.update({
            'latitude': latitude,
            'longitude': longitude,
            'caption': caption,
            'description': description
        })

        values.update(response)

        # Сохраняем фото в альбоме
        response = self.vk.method('photos.save', values)

        return response

    def photo_messages(self, photos):
        """ Загрузка изображений в сообщения

        :param photos: список путей к изображениям, либо путь к изображению
        """

        url = self.vk.method('photos.getMessagesUploadServer')['upload_url']

        photos_files = open_files(photos)
        response = self.vk.http.post(url, files=photos_files)
        close_files(photos_files)

        response = self.vk.method('photos.saveMessagesPhoto', response.json())

        return response

    def photo_profile(self, photo, owner_id=None, crop_x=None, crop_y=None, crop_width=None):
        """ Загрузка изображения профиля

        :param photo: путь к изображению
        :param owner_id: идентификатор сообщества или текущего пользователя.
                По умолчанию загрузка идет в профиль текущего пользователя.
                При отрицательном значении загрузка идет в группу.
        :param crop_x: координата X верхнего правого угла миниатюры.
        :param crop_y: координата Y верхнего правого угла миниатюры.
        :param crop_width: сторона квадрата миниатюры.
                При передаче всех crop_* для фотографии также будет подготовлена квадратная миниатюра.
        """

        values = {}

        if owner_id:
            values['owner_id'] = owner_id

        crop_params = {}

        if crop_x is not None and crop_y is not None and crop_width is not None:
            crop_params['_square_crop'] = '{0},{1},{2}'.format(crop_x, crop_y, crop_width)

        url = self.vk.method('photos.getOwnerPhotoUploadServer', values)['upload_url']

        photos_files = open_files(photo, key_format='file')
        response = self.vk.http.post(url, data=crop_params, files=photos_files)
        close_files(photos_files)

        response = self.vk.method('photos.saveOwnerPhoto', response.json())

        return response
    
    def photo_chat(self, photo, chat_id):
        """ Загрузка и смена обложки в беседе
        :param photo: путь к изображению
        :param chat_id: ID беседы
        """

        values = {'chat_id': chat_id}
        url = self.vk.method('photos.getChatUploadServer', values)['upload_url']

        photo_file = open_files(photo)
        response = self.vk.http.post(url, files=photo_file)
        close_files(photo_file)

        response = self.vk.method('messages.setChatPhoto', response.json())

        return response

    def photo_wall(self, photos, user_id=None, group_id=None):
        """ Загрузка изображений на стену пользователя или в группу

        :param photos: список путей к изображениям, либо путь к изображению
        :param user_id: идентификатор пользователя
        :param group_id: идентификатор сообщества (если загрузка идет в группу)
        """

        values = {}

        if user_id:
            values['user_id'] = user_id
        elif group_id:
            values['group_id'] = group_id

        response = self.vk.method('photos.getWallUploadServer', values)
        url = response['upload_url']

        photos_files = open_files(photos)
        response = self.vk.http.post(url, files=photos_files)
        close_files(photos_files)

        values.update(response.json())

        response = self.vk.method('photos.saveWallPhoto', values)

        return response

    def audio(self, file_path, **kwargs):
        """ Загрузка аудио

        :param file_path: путь к аудиофайлу
        :param artist: исполнитель
        :param title: название
        """

        url = self.vk.method('audio.getUploadServer')['upload_url']

        file = open_files(file_path, key_format='file')
        response = self.vk.http.post(url, files=file).json()
        close_files(file)

        response.update(kwargs)

        response = self.vk.method('audio.save', response)

        return response

    def document(self, file_path, title=None, tags=None, group_id=None):
        """ Загрузка документа

        :param file_path: путь к документу
        :param title: название документа
        :param tags: метки для поиска
        :param group_id: идентификатор сообщества (если загрузка идет в группу)
        """

        values = {'group_id': group_id}
        url = self.vk.method('docs.getUploadServer', values)['upload_url']

        with open(file_path, 'rb') as file:
            response = self.vk.http.post(url, files={'file': file}).json()

        response.update({
            'title': title,
            'tags': tags
        })

        response = self.vk.method('docs.save', response)

        return response


def open_files(paths, key_format='file{}'):
    if not isinstance(paths, list):
        paths = [paths]

    files = []

    for x, filename in enumerate(paths):
        file = open(filename, 'rb')

        ext = filename.split('.')[-1]
        files.append(
            (key_format.format(x), ('file{}.{}'.format(x, ext), file))
        )

    return files


def close_files(files):
    for file in files:
        file[1][1].close()
