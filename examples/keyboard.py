from vk_api import VkApi
from vk_api import VkKeyboard


vk = VkApi(token='your_api_token')

keyboard = VkKeyboard(one_time=True)

keyboard.add_line()  # Создание первой строки
keyboard.add_button('Белая кнопка', color='default')
keyboard.add_button('Зелёная кнопка', color='positive')

keyboard.add_line()  # Переход на вторую строку
keyboard.add_button('Красная кнопка', color='negative')

keyboard.add_line()  # Третья строка
keyboard.add_button('Синяя кнопка', color='primary')

vk.method('messages.send', {'peer_id': 123456,  # peer_id получателя
                            'message': 'Пример клавиатуры',
                            'keyboard': keyboard.get_keyboard()})
