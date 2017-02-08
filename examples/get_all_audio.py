#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

import vk_api


def getJson(file_name):
    with open(file_name) as file:
        json_text = json.loads(file.read())
    return json_text


def main():
    """ Пример получения последнего сообщения со стены """

    login, password = settings['vk']['login'], settings['vk']['pass']
    vk_session = vk_api.VkApi(login, password)

    try:
        vk_session.authorization()
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)
        return

    vk_audio = vk_api.VkAudio(vk_session)

    audio_list = vk_audio.get_all_audio_list('58895108')

    print("len: {}".format(len(audio_list)))
    for audio in audio_list:
        print("name: {0[0]}, url: {0[1]} ".format(audio))


if __name__ == '__main__':
    global settings
    settings = getJson('settings.json')
    main()