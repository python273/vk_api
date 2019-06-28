# -*- coding: utf-8 -*-
from flask import Flask
import vk_api

"""
Пример бота для группы ВКонтакте использующего
callback-api для получения сообщений.

Подробнее: https://vk.com/dev/callback_api

"""

app = Flask(__name__)
vk_session = vk_api.VkApi(token='your_group_token')
vk = vk_session.get_api()

access_code = "smthing code"

@app.route('/my_bot', methods=['POST'])
def bot():
    # получаем данные из запроса
    data = json.loads(request.data)
    # ВКонтакте в своих запросах всегда отправляет поле type:
    if 'type' not in data.keys():
        return 'not ok'

    # проверяем тип пришедшего события
    if data['type'] == 'confirmation':
        # если это запрос защитного кода
        # отправляем его
        return access_code
    # если же это сообщение, отвечаем пользователю
    elif data['type'] == 'message_new':
        # получаем ID пользователя
        from_id = data['object']['from_id']
        # отправляем сообщение
        vk.messages.send(message='Hello World!', random_id=0, peer_id=from_id)
        # возвращаем серверу VK "ok" и код 200
        return 'ok'

# точка входа приложения
if __name__ == '__main__':
    # запускаем веб-сервер
    app.run()
