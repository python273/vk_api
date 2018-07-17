import unittest

from vk_api import VkKeyboard
from vk_api.keyboard import KeyboardColor
from vk_api.utils import sjson_dumps

KEYBOARD_TEST = {
    'one_time': False,
    'buttons': [
        [
            {
                'color': 'default',
                'action': {
                    'type': 'text',
                    'payload': sjson_dumps({'test': 'some_payload'}),
                    'label': 'Test-1'
                }
            }
        ],
        []
    ]
}

EMPTY_KEYBOARD_TEST = {'one_time': False, 'buttons': []}


class TestKeyboard(unittest.TestCase):
    def setUp(self):
        self.keyboard = VkKeyboard()

    def test_keyboard(self):
        self.keyboard.add_button('Test-1',
                                 color=KeyboardColor.DEFAULT,
                                 payload={'test': 'some_payload'})
        self.keyboard.add_line()
        self.assertEqual(self.keyboard.get_keyboard(), sjson_dumps(KEYBOARD_TEST))

    def test_empty_keyboard(self):
        self.assertEqual(self.keyboard.get_empty_keyboard(), sjson_dumps(EMPTY_KEYBOARD_TEST))


if __name__ == '__main__':
    unittest.main()
