from vk_api.keyboard import VkKeyboard, VkKeyboardColor
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


keyboard = VkKeyboard()


def test_keyboard():
    keyboard.add_button(
        'Test-1',
        color=VkKeyboardColor.DEFAULT,
        payload={'test': 'some_payload'}
    )
    keyboard.add_line()
    assert keyboard.get_keyboard() == sjson_dumps(KEYBOARD_TEST)


def test_empty_keyboard():
    assert keyboard.get_empty_keyboard() == sjson_dumps(EMPTY_KEYBOARD_TEST)
