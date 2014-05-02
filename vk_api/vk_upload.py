# -*- coding: utf-8 -*-

"""
@author: Kirill Python
@contact: http://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2014
"""


class VkUpload(object):
    def __init__(self, vk):
        self.vk = vk
        # https://vk.com/dev/upload_files

    def photo(self, photos, album_id=None, group_id=None):
        """ Загрузка изображений в альбом пользователя

        photos = ['photo1.jpg', 'img.png']
               = 'screen.png'
               Максимум 5 фотографий

        album_id
        """

        if not (album_id and photos):
            return False

        if type(photos) == str:  # upload.photo('photo.jpg', ...)
            photos = [photos]

        values = {
            'album_id': album_id
        }
        if group_id:  # Если загружаем в группу
            values.update({'group_id': group_id})

        # Получаем ссылку для загрузки
        url = self.vk.method('photos.getUploadServer', values)['upload_url']

        # Загружаем
        photos_files = openPhotos(photos)
        response = self.vk.http.post(url, files=photos_files).json()
        closePhotos(photos_files)

        # Олег Илларионов:
        # это не могу к сожалению просто пофиксить
        if not 'album_id' in response:
            response['album_id'] = response['aid']

        # Сохраняем фото в альбоме
        response = self.vk.method('photos.save', response)

        return response

    def photoMessages(self, photos, group_id=None):
        """ Загрузка изображений в сообщения

        photos = ['photo1.jpg', 'img.png']
               = 'screen.png'
               Максимум 7(?) фотографий
        """

        if not photos:
            return False

        if type(photos) == str:  # upload.photo('photo.jpg', ...)
            photos = [photos]

        values = {}
        if group_id:
            values.update({'group_id': group_id})

        # Получаем ссылку для загрузки
        url = self.vk.method('photos.getMessagesUploadServer', values)
        url = url['upload_url']

        # Загружаем
        photos_files = openPhotos(photos)
        response = self.vk.http.post(url, files=photos_files)
        closePhotos(photos_files)

        # Сохраняем фото в альбоме
        response = self.vk.method('photos.saveMessagesPhoto', response.json())

        return response


def openPhotos(photos_paths):
    photos = {}

    for x, filename in enumerate(photos_paths):  # Открываем файлы
        photos.update(
            {'file%s' % x: open(filename, 'rb')}
        )

    return photos


def closePhotos(photos):
    for i in photos:
        photos[i].close()
