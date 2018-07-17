import unittest

from vk_api import VkKeyboard
from vk_api.keyboard import KeyboardColor

KEYBOARD_TEST = '{"one_time":false,"buttons":[[{"color":"default","action":{"type":"text","payload":"{\\"test\\":\\"some_payload\\"}","label":"Test-1"}}],[]]}'

EMPTY_KEYBOARD_TEST = '{"one_time":false,"buttons":[]}'


class TestKeyboard(unittest.TestCase):
    def setUp(self):
        self.keyboard = VkKeyboard()

    def test_keyboard(self):
        self.keyboard.add_button('Test-1',
                                 color=KeyboardColor.DEFAULT,
                                 payload={'test': 'some_payload'})
        self.keyboard.add_line()
        self.assertEqual(self.keyboard.get_keyboard(), KEYBOARD_TEST)

    def test_empty_keyboard(self):
        self.assertEqual(self.keyboard.get_empty_keyboard(), EMPTY_KEYBOARD_TEST)


if __name__ == "__main__":
    unittest.main()
