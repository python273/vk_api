# -*- coding: utf-8 -*-
"""
:authors: python273, Helow19274, prostomarkeloff
:license: Apache License, Version 2.0, see LICENSE file
:copyright: (c) 2019 python273
"""

from enum import Enum


from .utils import sjson_dumps


MAX_BUTTONS_ON_LINE = 5
MAX_DEFAULT_LINES = 10
MAX_INLINE_LINES = 6


class VkKeyboardColor(Enum):
    """ Возможные цвета кнопок """

    #: Синяя
    PRIMARY = 'primary'

    #: Белая
    SECONDARY = 'secondary'

    #: Красная
    NEGATIVE = 'negative'

    #: Зелёная
    POSITIVE = 'positive'


class VkKeyboardButton(Enum):
    """ Возможные типы кнопки """

    #: Кнопка с текстом
    TEXT = "text"

    #: Кнопка с местоположением
    LOCATION = "location"

    #: Кнопка с оплатой через VKPay
    VKPAY = "vkpay"

    #: Кнопка с приложением VK Apps
    VKAPPS = "open_app"

    #: Кнопка с ссылкой
    OPENLINK = "open_link"

    #: Callback-кнопка
    CALLBACK = "callback"


class VkKeyboard(object):
    """ Класс для создания клавиатуры для бота (https://vk.com/dev/bots_docs_3)
    :param one_time: Если True, клавиатура исчезнет после нажатия на кнопку
    :type one_time: bool
    """

    __slots__ = ('one_time', 'lines', 'keyboard', 'inline')

    def __init__(self, one_time=False, inline=False):
        self.one_time = one_time
        self.inline = inline
        self.lines = [[]]

        self.keyboard = {
            'one_time': self.one_time,
            'inline': self.inline,
            'buttons': self.lines
        }

    def get_keyboard(self):
        """ Получить json клавиатуры """
        return sjson_dumps(self.keyboard)

    @classmethod
    def get_empty_keyboard(cls):
        """ Получить json пустой клавиатуры.
        Если отправить пустую клавиатуру, текущая у пользователя исчезнет.
        """
        keyboard = cls()
        keyboard.keyboard['buttons'] = []
        return keyboard.get_keyboard()

    def add_button(self, label, color=VkKeyboardColor.SECONDARY, payload=None):
        """ Добавить кнопку с текстом.
            Максимальное количество кнопок на строке - MAX_BUTTONS_ON_LINE

        :param label: Надпись на кнопке и текст, отправляющийся при её нажатии.
        :type label: str
        :param color: цвет кнопки.
        :type color: VkKeyboardColor or str
        :param payload: Параметр для callback api
        :type payload: str or list or dict
        """

        current_line = self.lines[-1]

        if len(current_line) >= MAX_BUTTONS_ON_LINE:
            raise ValueError(f'Max {MAX_BUTTONS_ON_LINE} buttons on a line')

        color_value = color

        if isinstance(color, VkKeyboardColor):
            color_value = color_value.value

        if payload is not None and not isinstance(payload, str):
            payload = sjson_dumps(payload)

        button_type = VkKeyboardButton.TEXT.value

        current_line.append({
            'color': color_value,
            'action': {
                'type': button_type,
                'payload': payload,
                'label': label,
            }
        })

    def add_callback_button(self, label, color=VkKeyboardColor.SECONDARY, payload=None):
        """ Добавить callback-кнопку с текстом.
            Максимальное количество кнопок на строке - MAX_BUTTONS_ON_LINE

        :param label: Надпись на кнопке и текст, отправляющийся при её нажатии.
        :type label: str
        :param color: цвет кнопки.
        :type color: VkKeyboardColor or str
        :param payload: Параметр для callback api
        :type payload: str or list or dict
        """

        current_line = self.lines[-1]

        if len(current_line) >= MAX_BUTTONS_ON_LINE:
            raise ValueError(f'Max {MAX_BUTTONS_ON_LINE} buttons on a line')

        color_value = color

        if isinstance(color, VkKeyboardColor):
            color_value = color_value.value

        if payload is not None and not isinstance(payload, str):
            payload = sjson_dumps(payload)

        button_type = VkKeyboardButton.CALLBACK.value

        current_line.append({
            'color': color_value,
            'action': {
                'type': button_type,
                'payload': payload,
                'label': label,
            }
        })

    def add_location_button(self, payload=None):
        """ Добавить кнопку с местоположением.
            Всегда занимает всю ширину линии.

        :param payload: Параметр для callback api
        :type payload: str or list or dict
        """

        current_line = self.lines[-1]

        if len(current_line) != 0:
            raise ValueError(
                'This type of button takes the entire width of the line'
            )

        if payload is not None and not isinstance(payload, str):
            payload = sjson_dumps(payload)

        button_type = VkKeyboardButton.LOCATION.value

        current_line.append({
            'action': {
                'type': button_type,
                'payload': payload
            }
        })

    def add_vkpay_button(self, hash, payload=None):
        """ Добавить кнопку с оплатой с помощью VKPay.
            Всегда занимает всю ширину линии.

        :param hash: Параметры платежа VKPay и ID приложения
        (в поле aid) разделённые &
        :type hash: str
        :param payload: Параметр для совместимости со старыми клиентами
        :type payload: str or list or dict
        """

        current_line = self.lines[-1]

        if len(current_line) != 0:
            raise ValueError(
                'This type of button takes the entire width of the line'
            )

        if payload is not None and not isinstance(payload, str):
            payload = sjson_dumps(payload)

        button_type = VkKeyboardButton.VKPAY.value

        current_line.append({
            'action': {
                'type': button_type,
                'payload': payload,
                'hash': hash
            }
        })

    def add_vkapps_button(self, app_id, owner_id, label, hash, payload=None):
        """ Добавить кнопку с приложением VK Apps.
            Всегда занимает всю ширину линии.

        :param app_id: Идентификатор вызываемого приложения с типом VK Apps
        :type app_id: int
        :param owner_id: Идентификатор сообщества, в котором установлено
        приложение, если требуется открыть в контексте сообщества
        :type owner_id: int
        :param label: Название приложения, указанное на кнопке
        :type label: str
        :param hash: хэш для навигации в приложении, будет передан в строке
        параметров запуска после символа #
        :type hash: str
        :param payload: Параметр для совместимости со старыми клиентами
        :type payload: str or list or dict
        """

        current_line = self.lines[-1]

        if len(current_line) != 0:
            raise ValueError(
                'This type of button takes the entire width of the line'
            )

        if payload is not None and not isinstance(payload, str):
            payload = sjson_dumps(payload)

        button_type = VkKeyboardButton.VKAPPS.value

        current_line.append({
            'action': {
                'type': button_type,
                'app_id': app_id,
                'owner_id': owner_id,
                'label': label,
                'payload': payload,
                'hash': hash
            }
        })

    def add_openlink_button(self, label, link, payload=None):
        """ Добавить кнопку с ссылкой
            Максимальное количество кнопок на строке - MAX_BUTTONS_ON_LINE

        :param label: Надпись на кнопке
        :type label: str
        :param link: ссылка, которую необходимо открыть по нажатию на кнопку
        :type link: str
        :param payload: Параметр для callback api
        :type payload: str or list or dict
        """
        current_line = self.lines[-1]

        if len(current_line) >= MAX_BUTTONS_ON_LINE:
            raise ValueError(f'Max {MAX_BUTTONS_ON_LINE} buttons on a line')

        if payload is not None and not isinstance(payload, str):
            payload = sjson_dumps(payload)

        button_type = VkKeyboardButton.OPENLINK.value

        current_line.append({
            'action': {
                'type': button_type,
                'link': link,
                'label': label,
                'payload': payload
            }
        })

    def add_line(self):
        """ Создаёт новую строку, на которой можно размещать кнопки.
            Максимальное количество строк:
               Стандартное отображение - MAX_DEFAULT_LINES;
               Inline-отображение - MAX_INLINE_LINES.
        """
        if self.inline:
            if len(self.lines) >= MAX_INLINE_LINES:
                raise ValueError(f'Max {MAX_INLINE_LINES} lines for inline keyboard')
        else:
            if len(self.lines) >= MAX_DEFAULT_LINES:
                raise ValueError(f'Max {MAX_DEFAULT_LINES} lines for default keyboard')

        self.lines.append([])
