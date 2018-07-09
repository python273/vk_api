# -*- coding: utf-8 -*-
import vk_api
from vk_api.keyboard import KeyboardColor


def main():
    """ Пример создания клавиатуры для отправки ботом """

    vk_session = vk_api.VkApi(token='bot_api_token')
    vk = vk_session.get_api()

    keyboard = vk_api.VkKeyboard(one_time=True)

    keyboard.add_button('Белая кнопка', color=KeyboardColor.DEFAULT)
    keyboard.add_button('Зелёная кнопка', color=KeyboardColor.POSITIVE)

    keyboard.add_line()  # Переход на вторую строку
    keyboard.add_button('Красная кнопка', color=KeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Синяя кнопка', color=KeyboardColor.PRIMARY)

    vk.messages.send(
        peer_id=123456,
        message='Пример клавиатуры',
        keyboard=keyboard.get_keyboard()
    )


if __name__ == '__main__':
    main()
