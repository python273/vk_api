# -*- coding: utf-8 -*-
import collections
import vk_api


def main():
    """ Пример составления топа исполнителей для профиля вк """

    login, password = 'login', 'password'
    vk_session = vk_api.VkApi(login, password)

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vkaudio = vk_session.get_audio()

    """
        VkApi.audio.get и VkApi.audio.search делает запросы к странице m.vk.com
        и извлекает информацию из html. Необходимый параметр для метода search - 'q',
        а для get - 'owner_id'. Параметр offset принимает стандартное значение - 0.
        Здесь мы получим все аудиозаписи пользователя в цикле с использованием параметра offset
        и составим рейтинг самых популярных исполнителей для данного профиля.
        Ниже мы выведем список из 10 песен самого популярного
    """

    count = 0
    artists = collections.Counter()
    while True:
        audios = vkaudio.get(owner_id=-99463083, offset=count)
        print('offset=', count)
        for audio in audios:
            artists[audio['artist']] += 1

        count += len(audios)

        if len(audios) == 0:
            break

    # состаляем рейтинг первых 15
    print('\nTop 15:')
    for artist, tracks in artists.most_common(15):
        print('{} - {} tracks added'.format(artist, tracks))

    # ищем треки самого популярного
    most_common = artists.most_common(1)[0][0]
    print('\nSearch for ', most_common)
    tracks = vkaudio.search(q=most_common)
    for n, track in enumerate(tracks[:10]):
        print('{}. {}\nURL: {}'.format(n+1, track['title'], track['url']))

if __name__ == '__main__':
    main()
