# -*- coding: utf-8 -*-
import collections

import vk_api
from vk_api.audio import VkAudio


def main():
    """ Пример составления топа исполнителей для альбома вк """

    login, password = 'login', 'password'
    vk_session = vk_api.VkApi(login, password)

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vkaudio = VkAudio(vk_session)

    artists = collections.Counter()

    offset = 0

    while True:
        albums = vkaudio.get(owner_id='194957739', get_albums=True, offset=offset)

        if not albums:
            break

        for album in albums:
            artists[album['artist']] += 1

        offset += len(albums)

    # Составляем рейтинг первых 15
    print('\nTop 15:')
    for artist, tracks in artists.most_common(15):
        print('{} - {} tracks'.format(artist, tracks))

    # Ищем треки последнего альбома
    album = vkaudio.get(owner_id='194957739', get_albums=True)[0]
    print('\nSearch for', album['title'])

    tracks = vkaudio.get(album_id=album['id'][25:])

    for n, track in enumerate(tracks, 1):
        print('{}. {} {}'.format(n, track['title'], track['url']))


if __name__ == '__main__':
    main()
