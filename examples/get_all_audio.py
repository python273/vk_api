#!/usr/bin/python3
# -*- coding: utf-8 -*-

import vk_api

def main():
    """ Пример получения списка всех песен по id """

    login, password = 'python@vk.com', 'mypassword'
    vk_session = vk_api.VkApi(login, password)

    try:
        vk_session.authorization()
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)
        return

    vk_audio = vk_api.VkAudio(vk_session)

    audio_list = vk_audio.get_all_audio_list('12345678')

    print("len: {}".format(len(audio_list)))
    for audio in audio_list:
        print("name: {0[0]}, url: {0[1]} ".format(audio))


if __name__ == '__main__':
    global settings
    main()