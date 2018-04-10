import vk_api
import requests
import json
import logging
from vk_api.longpoll import VkLongPoll, VkEventType
from history_dumper.db_work import*

logger = logging.getLogger("LOG")

class VKHistoryDumper:
    def __init__(self, settings):
        self.settings = settings

    def __enter__(self):
        self.start()

    def __exit__(self, type, value, traceback):
        pass

    def start(self):
        logger.debug("VKHistory Dumper start")

        db_work = DBWork(self.settings['DATABASE'],
                         self.settings['USER'],
                         self.settings['HOST'],
                         self.settings['PORT'],
                         self.settings['PASSWORD_DB'])

        db_work.create_last_msg_table()

        logger.info("Initialize work with database. Database: %s." + \
                    ". User: %s. Host: %s.",
                     self.settings['DATABASE'],
                     self.settings['USER'],
                     self.settings['HOST'])

        try:
            # Авторизация
            vk_session = vk_api.VkApi(self.settings['VK_LOGIN'], 
                                      self.settings['VK_PASSWORD'])
            vk = vk_session.get_api()
            vk_session.auth(token_only=True)
        except vk_api.AuthError as error_msg:
            logger.critical('%s', error_msg)
            return
        try:
            tools = vk_api.VkTools(vk_session)
            # Получение информации о текущем пользователе
            uid = vk.users.get()[0]['id']
            logger.debug("User id: %s", uid)

            # Получение последнего идентификатора сообщения из БД, либо None
            # в случае отсутствия uid в БД
            last_msg_id = db_work.get_latest_msg_id(uid)
            logger.debug("Latest message id: %s", last_msg_id)
            if last_msg_id == None:
                last_msg_id = 0

            # Получение списка диалогов
            dialogs = tools.get_all('messages.getDialogs', 200)
            if dialogs['count'] > 0:
                last_msg_id_curr = dialogs['items'][0]['message']['id']
                if last_msg_id_curr > last_msg_id:
                    db_work.update_latest_msg_id(uid, last_msg_id_curr)
                    for dialog in dialogs['items']:
                        message = dialog['message']
                        if 'chat_id' in message:
                            user_id = 2000000000 + message['chat_id']
                        else:
                            user_id = message['user_id']
                        if last_msg_id != 0:
                            messages = tools.get_all('messages.getHistory', 200,
                                                    {'user_id': user_id,
                                                     'start_message_id': 
                                                     last_msg_id},
                                                     negative_offset=True)
                        else:
                            messages = tools.get_all('messages.getHistory', 200,
                                                    {'user_id': user_id})
                        # Обработка диалога
                        if messages["count"] > 0:
                            self.process_dialog(messages)
            return True
        except vk_api.exceptions.ApiError:
            logger.critical("Exception: ApiError")
            return False

    def process_dialog(self, messages):
        logger.info('%s', json.dumps(messages, ensure_ascii=False, indent=4))