from enum import Enum
from .utils import sjson_dumps


class KeyboardColors(Enum):
    """ Допустимые цвета кнопок.
    """
    PRIMARY = 'primary'    # синяя
    DEFAULT = 'default'    # белая
    NEGATIVE = 'negative'  # красная
    POSITIVE = 'positive'  # зелёная


class VkKeyboard(object):
    """
    :param one_time: Если True, клавиатура исчезнет сразу после нажатия на кнопку.
    :type one_time: bool
    """
    def __init__(self, one_time=False):
        self.keyboard = {}
        self.keyboard['one_time'] = one_time
        self.keyboard['buttons'] = []
        self.keyboard['buttons'].append([])

        self.line = 0

    def get_keyboard(self):
        """ Возвращает json клавиатуры
        """
        return sjson_dumps(self.keyboard)

    @classmethod
    def get_empty_keyboard(cls):
        """ Возвращает json пустой клавиатуры.
            Если отправить пустую клавиатуру, текущая у пользователя исчезнет.
        """
        keyboard = cls()
        keyboard.keyboard['buttons'] = []
        return keyboard.get_keyboard()

    def add_button(self, label, color='default', payload=None):
        """
        :param label: Надпись на кнопке и текст, отправляющийся при её нажатии.

        :param color: цвет кнопки.
            См. :class:`KeyboardColors`

        :param payload: Параметр для callback api

        Максимальное количество кнопок на строке - 4
        """
        button = {}
        button['action'] = {}
        button['action']['type'] = 'text'
        button['action']['payload'] = payload
        button['action']['label'] = label
        button['color'] = color
        self.keyboard['buttons'][self.line].append(button)

    def add_line(self):
        """ Создаёт новую строчку, на которой можно размещать кнопки.
            Максимальное количество строк - 10
        """
        self.line += 1
        self.keyboard['buttons'].append([])
