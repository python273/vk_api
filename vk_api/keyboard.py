import json


class VkKeyboard(object):
    """
    :param one_time: Если True, клавиатура исчезнет сразу после нажатия на кнопку.
    :type one_time: bool
    """
    def __init__(self, one_time=False):
        self.keyboard = {}
        self.keyboard['one_time'] = one_time
        self.keyboard['buttons'] = []
        self.line = None

    def get_keyboard(self):
        """ Возвращает json клавиатуры
        """
        return json.dumps(self.keyboard, ensure_ascii=False)

    def get_empty_keyboard(self):
        """ Возвращает json пустой клавиатуры.
            Если отправить пустую клавиатуру, текущая у пользователя исчезнет.
        """
        empty_keyboard = self.keyboard
        empty_keyboard['buttons'] = []
        return json.dumps(empty_keyboard, ensure_ascii=False)

    def add_button(self, label, color='default', payload=None):
        """
        :param label: Надпись на кнопке и текст, отправляющийся при её нажатии.

        :param color: цвет кнопки.
            Бывает default(белая), primary(синяя), positive(зелёная) и negative(красная).

        :param payload: Параметр для callback api

        Максимальное количество кнопок на строке - 4
        """
        button = {}
        button['action'] = {}
        button['action']['type'] = 'text'
        button['action']['payload'] = payload
        button['action']['label'] = label
        button['color'] = color
        self.keyboard['buttons'][self.line - 1].append(button)

    def add_line(self):
        """ Создаёт новую строчку, на которой можно размещать кнопки.
            Максимальное количество строк - 10
        """
        if not self.line:
            self.line = 1
        else:
            self.line += 1

        self.keyboard['buttons'].append([])
