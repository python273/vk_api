import os
import unittest

from vk_api import VkApi, audio


vk_session = VkApi(
    login=os.environ['LOGIN'],
    password=os.environ['PASSWORD']
)
vk_session.auth()
vk_audio = audio.VkAudio(vk_session)


def test_audio_generator():
    for i in vk_audio.search('киш'):
        assert type(i) is list
        break
    else:
        assert False


if __name__ == '__main__':
    unittest.main()
