# -*- coding: utf-8 -*-

import vk_api
from vk_api.audio import VkAudio


def main():
    """ Пример отображения 5 последних альбомов пользователя """

    login, password = 'login', 'password'
    vk_session = vk_api.VkApi(login, password)

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vkaudio = VkAudio(vk_session)

    albums = []
    offset = 0

    while True:
        temp_albums = vkaudio.get_albums(owner_id='194957739', offset=offset)

        if not temp_albums:
            break

        albums += temp_albums
        offset += len(temp_albums)

    print('\nLast 5:')
    for album in albums[:5]:
        print(album['title'])

    # Ищем треки последнего альбома
    print('\nSearch for', albums[0]['title'])
    tracks = vkaudio.get(album_id=albums[0]['id'])

    for n, track in enumerate(tracks, 1):
        print('{}. {} {}'.format(n, track['title'], track['url']))


if __name__ == '__main__':
    main()
