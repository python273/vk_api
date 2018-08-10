# -*- coding: utf-8 -*-
import vk_api
from vk_api.streaming import VkStreaming


def main():
    """ Пример использования streaming
	    https://vk.com/dev/streaming_api_docs
    """
    vk = vk_api.VkApi(token=<Сервисный ключ доступа>)
    streaming = VkStreaming(vk)

    streaming.delete_all_rules()

    streaming.add_rule("квартира Москва", "Квартиры")
    streaming.add_rule("купить гараж", "Гаражи")

    for event in streaming.listen():
        tags = '|'.join(event['tags'])
        print("Теги: " + tags)
        print("Запись: " + event['event_url'])
        print("Текст: " + event['text'])
        print("_____________________________________________________")

if __name__ == '__main__':
	main()
