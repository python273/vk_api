import vk_api


def main():
    vk = vk_api.VkApi(token='your_api_token')

    keyboard = vk_api.VkKeyboard(one_time=True)

    Colors = vk_api.keyboard.KeyboardColors

    keyboard.add_button('Белая кнопка', color=Colors.DEFAULT.value)
    keyboard.add_button('Зелёная кнопка', color=Colors.POSITIVE.value)

    keyboard.add_line()  # Переход на вторую строку
    keyboard.add_button('Красная кнопка', color=Colors.NEGATIVE.value)

    keyboard.add_line()  # Третья строка
    keyboard.add_button('Синяя кнопка', color=Colors.PRIMARY.value)

    vk.method('messages.send', {'peer_id': 123456,  # peer_id получателя
                                'message': 'Пример клавиатуры',
                                'keyboard': keyboard.get_keyboard()})


if __name__ == '__main__':
    main()
