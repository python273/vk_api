# -*- coding: utf-8 -*-
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

    vk = vk_session.get_api()

    """
        VkApi.audio.get и VkApi.audio.search делает запросы к странице m.vk.com
        и извлекает информацию из html. Необходимый параметр для метода search - 'q',
        а для get - 'owner_id'. Параметр offset принимает стандартное значение - 0.
        Здесь мы получим все аудиозаписи пользователя в цикле с использованием параметра offset
        и составим рейтинг самых популярных исполнителей для данного профиля.
        Ниже мы выведем список из 10 песен самого популярного
    """

    count = 0
    artists = {}
    while True:
        audios = vk.audio.get(owner_id=19688539, offset=count)
        print('offset=', count)
        for audio in audios:
            try:
                artists[audio['artist']] += 1
            except KeyError:
                artists[audio['artist']] = 1

        count += len(audios)

        if len(audios) == 0:
            break

    # состаляем рейтинг первых 15
    sorted_artists = sorted(artists, key=artists.get, reverse=True)
    for artist in sorted_artists[:15]:
        print('{} - {} tracks added'.format(artist, artists[artist]))

    # ищем треки самого популярного
    tracks = vk.audio.search(q=sorted_artists[0])
    for n, track in enumerate(tracks[:10]):
        print('{}. {}'.format(n+1, track['title']))

if __name__ == '__main__':
    main()
