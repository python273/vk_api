# -*- coding: utf-8 -*-
"""
:authors: python273
:contact: https://vk.com/python273
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2018 python273
"""

"""
Заготовка, к сожалению не понимаю как впихнуть этот способ в vk_api
Думаю что можно вынести в отдельный класс и добавить обработчик
Можно было бы засунуть в longpoll.py, но хочется что бы это работало и вне longpoll-а
Надеюсь кто нибудь придумает как это реализовать без костылей
"""
class StepHandler(object):
    def __init__(self):
            # key: user_id, value: handler list
            self.next_step_handlers = {}
    
    def register(self, user_id, message, callback, *args, **kwargs):
        """
        Регистрирует функцию обратного вызова, которая будет уведомляться, когда новое сообщение приходит после `message`.

        :param message:     Сообщение, после которого мы хотим обрабатывать новое сообщение в одном чате.
        :param user_id      Пользователь для которого мы регистрируем callback функцию
		:param callback:    Функция, куда приходит следующее сообщение.
        :param args:        Аргументы передаваемые в callback функцию
        :param kwargs:      Аргументы передаваемые в callback функцию
        """
        if user_id in self.next_step_handlers.keys():
            self.next_step_handlers[user_id_id].append({"callback": callback, "args": args, "kwargs": kwargs})
        else:
            self.next_step_handlers[user_id_id] = [{"callback": callback, "args": args, "kwargs": kwargs}]
    
    def clear(self, user_id):
        """
        Удаляет все зарегистрированные callback функций

        :param user_id:     Пользователь для которого мы хотим отчистить next_step_handlers
        """
        self.next_step_handlers[chat_id] = []