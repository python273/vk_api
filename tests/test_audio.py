import os
import unittest

from vk_api import VkApi, audio


class TestAudio(unittest.TestCase):
    def setUp(self):
        self.vk_session = VkApi(
            login=os.environ['LOGIN'],
            password=os.environ['PASSWORD']
        )
        self.vk_session.auth()
        self.vk_audio = audio.VkAudio(self.vk_session)

    def test_audio(self):
        audio_list = self.vk_audio.search('киш')
        self.assertEqual(type(audio_list), list)

    def test_audio_generator(self):
        for i in self.vk_audio.search('киш', first=False):
            self.assertEqual(type(i), list)
            break
        else:
            self.assertEqual(False, True)


if __name__ == '__main__':
    unittest.main()
