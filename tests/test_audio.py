import os

from vk_api import VkApi, audio


vk_session = VkApi(
    login=os.environ['LOGIN'],
    password=os.environ['PASSWORD']
)
vk_session.auth()
vk_audio = audio.VkAudio(vk_session)


def test_audio_generator():
    for _ in vk_audio.search_iter('киш'):
        assert True
        break
    else:
        assert False


def test_audio_seacrh_user():
    for i in vk_audio.search_user():
        print()
    print()
