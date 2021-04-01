# -*- coding: utf-8 -*-
import vk_api, traceback
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from requests.exceptions import RequestException

def connect():
    
    vk_session = vk_api.VkApi(token='your_group_token')
    longpoll = VkBotLongPoll(vk_session, 'your_group_id')

def main():
    """ Пример использования bots longpoll

        https://vk.com/dev/bots_longpoll
    """
    connect()
    
    while True:
        try:
            
            for event in longpoll.listen():

                if event.type == VkBotEventType.MESSAGE_NEW:
                    print('Новое сообщение:')

                    print('Для меня от: ', end='')

                    print(event.obj.from_id)

                    print('Текст:', event.obj.text)
                    print()

                elif event.type == VkBotEventType.MESSAGE_REPLY:
                    print('Новое сообщение:')

                    print('От меня для: ', end='')

                    print(event.obj.peer_id)

                    print('Текст:', event.obj.text)
                    print()

                elif event.type == VkBotEventType.MESSAGE_TYPING_STATE:
                    print('Печатает ', end='')

                    print(event.obj.from_id, end=' ')

                    print('для ', end='')

                    print(event.obj.to_id)
                    print()

                elif event.type == VkBotEventType.GROUP_JOIN:
                    print(event.obj.user_id, end=' ')

                    print('Вступил в группу!')
                    print()

                elif event.type == VkBotEventType.GROUP_LEAVE:
                    print(event.obj.user_id, end=' ')

                    print('Покинул группу!')
                    print()

                else:
                    print(event.type)
                    print()
            
            except RequestException:
                """Переподключение в случае долгой неактивности или перезагрузки серверов"""
                
                connect()

if __name__ == '__main__':
    main()
